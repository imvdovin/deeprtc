from pathlib import Path
from deeprtc.modules.asr.predict import ASR
from deeprtc.modules.file.repository import FileRepository
from deeprtc.modules.file.dto.update_audio_text_token_dto import UpdateAudioTextTokenDto


class ASRService:
    def __init__(self):
        self.asr = ASR()
        self.file_repository = FileRepository()

    async def transcribe(self, file_path: Path, object_id):
        predict = self.asr.recognize(file_path)

        text = predict['utterance']

        update_dto = UpdateAudioTextTokenDto(text=text, transcribed=True)

        await self.file_repository.update({'_id': object_id}, update_dto)
