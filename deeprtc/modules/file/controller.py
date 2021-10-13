from fastapi import APIRouter, File, UploadFile
from fastapi.param_functions import Depends
from modules.asr.service import ASRService
from modules.file.service import FileService


router = APIRouter(prefix='files', tags=['files'])


@router.post('/')
async def post_audio(
        audio_file: UploadFile = File(),
        asr_service: ASRService = Depends(ASRService),
        file_service: FileService = Depends(FileService)):
    file_path = await file_service.save(audio_file)
    text = asr_service.transcribe(file_path)
    return {'text': text}
