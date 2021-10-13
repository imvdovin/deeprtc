from nemo.collections import asr
from common.settings import asr_model


class ASRService:
    def __init__(self):
        self.asr_model = asr_model

    def transcribe(self, filename):
        return self.asr_model.transcribe(filename)
