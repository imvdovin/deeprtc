from fastapi.param_functions import File
import pytest
from fastapi import UploadFile
from ...modules.file.service import FileService


file_service = FileService()


@pytest.mark.anyio
async def test_file_service_save():
    file = UploadFile(filename='test.wav')

    file_path = await file_service.save(file)

    assert file_path is not None
