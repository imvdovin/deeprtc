from pathlib import Path
import torch
import torch
from common.settings import model, processor


class ASRService:
    def __init__(self):
        self.asr_model = model

    def transcribe(self, file, device='cpu'):
        inputs = processor(file,
                           sampling_rate=16_000,
                           return_tensors="pt",
                           padding=True)

        with torch.no_grad():
            logits = model(inputs.input_values.to(device),
                           attention_mask=inputs.attention_mask.to(device)).logits
            pred_ids = torch.argmax(logits, dim=-1)
        predict = processor.batch_decode(pred_ids)[0].replace("<s>", "")
        return predict
    # return self.asr_model.transcribe(paths2audio_files=[str(file_path.resolve())])
