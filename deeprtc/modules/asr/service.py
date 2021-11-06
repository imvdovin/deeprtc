import asyncio
import requests
import logging
from deeprtc.common.settings import media_folder
from deeprtc.modules.asr.predict import ASR
from deeprtc.modules.file.repository import FileRepository
from deeprtc.modules.file.dto.update_audio_text_token_dto import UpdateAudioTextTokenDto
from deeprtc.common.settings import get_settings
from bson import ObjectId


logger = logging.getLogger(__file__)


class ASRService:
    def __init__(self):
        self.asr = ASR()
        self.file_repository = FileRepository()
        self.settings = get_settings()

    def transcribe(self, file_name: str, object_id: str):
        file_path = media_folder / file_name

        predict = self.asr.recognize(file_path.resolve())

        text = predict['utterance']

        data = {'x': [text]}

        try:
            resp = requests.post(
                url=self.settings.spellchecker_url, json=data)

            if resp.status_code != 200:
                raise Exception(
                    f'Spellchecker service unavailable. Code: {resp.status_code}')

            resp_encoded = resp.json()

            if len(resp_encoded[0]) > 0 \
                    and len(resp_encoded[0][0]) > 0:
                text = resp_encoded[0][0]
                logger.info(f'Spell checker text: {text}')
        except Exception as err:
            logger.error(err)

        update_dto = UpdateAudioTextTokenDto(
            text=text, time_steps=predict['time_steps'], transcribed=True)

        loop = asyncio.get_event_loop()

        coroutine = self.file_repository.update(
            {'_id': ObjectId(object_id)}, update_dto)

        loop.run_until_complete(coroutine)
