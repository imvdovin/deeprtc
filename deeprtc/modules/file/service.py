import functools
import pydub
import docx
from uuid import uuid4
from io import BytesIO
from pathlib import Path
from fastapi import UploadFile
from deeprtc.common.settings import get_settings
from deeprtc.modules.file.exceptions.http_unsupported_extension import UnsupportedExtensionHttpException
from deeprtc.modules.file.repository import FileRepository
from deeprtc.modules.file.dto.create_audio_text_token_dto import CreateAudioTextTokenDto
from deeprtc.modules.file.types import SaveFileResult


def media_path_defined():
    settings = get_settings()

    def inner_function(func):
        @functools.wraps(func)
        async def wrapped(*args):
            media_path = Path(settings.save_folder)

            if not media_path.is_dir():
                media_path.mkdir()

            return await func(*args)
        return wrapped
    return inner_function


class FileService:
    def __init__(self):
        self.settings = get_settings()
        self.repository = FileRepository()

    @media_path_defined()
    async def save(self, file: UploadFile) -> SaveFileResult:
        *file_name, file_ext = file.filename.split('.')

        if file_ext == '' or file_ext is None:
            raise UnsupportedExtensionHttpException()

        generated_name = '{0}.{1}'.format(uuid4().hex, file_ext)
        dest = Path(self.settings.save_folder) / generated_name

        audio_obj = pydub.AudioSegment.from_wav(file.file)

        transformed_audio = audio_obj.set_channels(
            1).set_frame_rate(16000).set_sample_width(2)

        transformed_audio.export(str(dest), format='wav')

        return SaveFileResult(path=dest, name=generated_name)

    def create_word_by_text(self, text: str) -> BytesIO:
        doc: docx.Document = docx.Document()
        doc.add_paragraph(text)

        doc_stream = BytesIO()

        doc.save(doc_stream)

        return doc_stream

    async def create_token_for_transcribed_audio(
            self,
            file_name: str):
        create_dto = CreateAudioTextTokenDto(file_name=file_name)
        return await self.repository.create(create_dto)
