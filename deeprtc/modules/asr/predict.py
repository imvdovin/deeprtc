from pathlib import Path
import itertools
from dataclasses import dataclass
from typing import Generator, Union, Dict
from typing import List, Optional
import numpy as np
import torch
import torchaudio
from deeprtc.common.settings import model, processor, gpu_usage

import logging
logger = logging.getLogger('uvicorn.access')


@dataclass
class Word:
    word: str
    start_time: float
    end_time: float

    def shift(self, offset: float):
        return Word(self.word, self.start_time + offset, self.end_time + offset)


class ASR:
    def __init__(self):
        self.device = gpu_usage if torch.cuda.is_available() else 'cpu'
        # self.model = Wav2Vec2ForCTC.from_pretrained(path_to_model).to(device)
        # self.processor = Wav2Vec2Processor.from_pretrained(path_to_model)
        self.model = model
        self.processor = processor
        self.SAMPLE_RATE = 16000
        self.MIN_PART_LENGTH = int(0.1 * self.SAMPLE_RATE)
        self.pad_list = list(range(0,320,320//2))

    @staticmethod
    def _to_tensor(x: Union[np.ndarray, torch.Tensor]):
        if isinstance(x, torch.Tensor):
            t = x
        else:
            t = torch.from_numpy(x)
        return t.float()

    def load_wav(self, fpath_or_wav: Union[str, Path, np.ndarray]) -> torch.Tensor:
        """
        Reads the file and converts the data into the format suited for recognition
        """
        # Load the wav from disk if needed
        if isinstance(fpath_or_wav, str) or isinstance(fpath_or_wav, Path):
            try:
                speech_array, sampling_rate = torchaudio.load(fpath_or_wav)
            except Exception as e:
                raise ValueError(f'Invalid load file: {fpath_or_wav} \n {e}')

            if sampling_rate != self.SAMPLE_RATE:
                resampler = torchaudio.transforms.Resample(
                    sampling_rate, self.SAMPLE_RATE)
                speech_array = resampler(speech_array)
        else:
            speech_array = fpath_or_wav
        t = self._to_tensor(speech_array)
        if t.size(0) > 1:
            t = t.sum(dim=0, keepdim=True)
        return t.squeeze()

    def split_to_chunks(self, source: Union[np.ndarray, torch.Tensor],
                        window_size: int = int(0.2 * 16000),
                        window_step: int = int(0.1 * 16000),
                        silence_quantile: float = .25,
                        min_length: int = int(10 * 16000),
                        max_length: int = int(20 * 16000)) -> Generator[torch.Tensor, None, None]:
        """
        Iterates over an audio file splitting it into relatively small parts
        :param source: source data (one channel)
        :param window_size: the size of the rectangular window that is used for calculating "energy" levels
        :param window_step: the windows moves over the data using this value
        :param silence_quantile: is used to determine the silence threshold
        :param min_length: minimum part length (in samples)
        :param max_length: maximum part length (in samples)
        :return: part tensor
        """

        assert window_size > 0
        assert 0 < window_step <= window_size
        assert 0 < silence_quantile < 1
        assert min_length <= max_length
        assert min_length > window_size

        def level(x: torch.Tensor):
            return torch.abs(x).sum()

        x = self._to_tensor(source)
        if len(x) <= min_length:
            yield x
        else:
            threshold = torch.quantile(
                torch.Tensor([level(x[i:i + window_size])
                             for i in range(1, len(x) - window_size + 1, window_step)]),
                silence_quantile
            )

            start = 0
            while start < len(x):
                if start + max_length >= len(x):
                    finish = len(x)
                else:
                    finish = start + min_length
                    while finish < start + max_length:
                        if level(x[finish - window_size:finish]) <= threshold:
                            break

                        finish += window_step

                    finish = min(finish, start + max_length)

                yield x[start:finish]
                start = finish

    def predict_model(self, source: torch.Tensor) -> torch.Tensor:
        batch = [torch.hstack((torch.zeros(pad), source)).numpy() for pad in self.pad_list]
        inputs = self.processor(batch,
                                sampling_rate=self.SAMPLE_RATE,
                                return_tensors="pt",
                                padding=True)
        with torch.no_grad():
            predict = self.model(inputs.input_values.to(self.model.device),
                                 attention_mask=inputs.attention_mask.to(self.model.device)).logits.cpu()
        return predict

    @staticmethod
    def find_words(tokens: List[str],
                   length: float = 0,
                   blank=processor.tokenizer.pad_token,
                   separator: str = '|') -> List[Word]:
        words: List[Word] = []

        token_length = length / len(tokens)
        start: Optional[int] = None
        for i, token in enumerate(tokens):
            if start is None and token not in (blank, separator):
                start = i
            if start is not None and token == separator:
                word_tokens = [g[0] for g in itertools.groupby(
                    tokens[start:i]) if g[0] != blank]
                if len(word_tokens) > 0:
                    finish = i
                    while tokens[finish - 1] == blank:
                        finish -= 1

                    words.append(Word(''.join(word_tokens).lower(),
                                 start * token_length, finish * token_length))
                start = None

        return words

    @staticmethod
    def get_utterance(words: List[Word]) -> str:
        return ' '.join([w.word for w in words])

    def decode_words(self,
                     prediction: Union[np.ndarray, torch.Tensor],
                     part_length: float) -> List[Word]:
        """
        Convert model predict to words.
        """
        pred_ids = torch.argmax(prediction, dim=-1)
         # выбираем лучшего кандидата по длине
        predict = self.processor.tokenizer.batch_decode(pred_ids)
        len_list = list(map(len, predict))
        max_value = max(len_list)
        max_index = len_list.index(max_value)
        # отправляем в декодирование лучшее распознование
        tokens = self.processor.tokenizer.convert_ids_to_tokens(
            pred_ids[max_index].squeeze())
        part_words = self.find_words(tokens, part_length)

        return part_words

    def recognize(self, source: Union[str, Path, np.ndarray]) -> Dict[str, List[Dict[str, float]]]:
        """
        Main function for recognize file or waveform.
        """
        wav = self.load_wav(source)
        result = {}
        words = []
        part_offset = 0.0

        for part in self.split_to_chunks(wav):
            if len(part) < self.MIN_PART_LENGTH:
                logger.warning(
                    'The part is too short (%d), discard, ', len(part))
                break

            part_length = len(part) / self.SAMPLE_RATE
            prediction = self.predict_model(part)
            part_words = self.decode_words(prediction, part_length)
            words += [w.shift(part_offset) for w in part_words]

            part_offset += part_length

        result['utterance'] = self.get_utterance(words)
        result['time_steps'] = [
            {'word': w.word, 'start_time': w.start_time, 'end_time': w.end_time} for w in words]

        logger.debug('Utterance: %s', result['utterance'])
        return result
