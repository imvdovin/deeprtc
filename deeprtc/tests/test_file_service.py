import pytest
import os
from fastapi import UploadFile
from modules.file.service import FileService


file_service = FileService()


@pytest.mark.asyncio
async def test_file_service_save():
    file = UploadFile(filename='test.wav')

    file_path = await file_service.save(file)

    assert file_path is not None

    os.remove(file_path)
