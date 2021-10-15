import aiofiles
import functools
import pydub
from uuid import uuid4
from pathlib import Path
from fastapi import UploadFile
from common.settings import get_settings
from modules.file.exceptions.http_unsupported_extension import UnsupportedExtensionHttpException


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

    @media_path_defined()
    async def save(self, file: UploadFile):
        *file_name, file_ext = file.filename.split('.')

        if file_ext == '' or file_ext is None:
            raise UnsupportedExtensionHttpException()

        generated_name = '{0}.{1}'.format(uuid4().hex, file_ext)
        dest = Path(self.settings.save_folder) / generated_name

        audio_obj = pydub.AudioSegment.from_wav(file.file)

        transformed_audio = audio_obj.set_channels(
            1).set_frame_rate(44100).set_sample_width(2)

        transformed_audio.export(str(dest), format='wav')

        return transformed_audio.get_array_of_samples()
