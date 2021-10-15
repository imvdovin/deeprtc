from fastapi import APIRouter, File, UploadFile
from fastapi.param_functions import Depends
from modules.asr.service import ASRService
from modules.file.service import FileService


router = APIRouter(tags=['files'])


@router.post('/')
async def post_audio(
        audio_file: UploadFile = File(...),
        asr_service: ASRService = Depends(ASRService),
        file_service: FileService = Depends(FileService)):
    file = await file_service.save(audio_file)
    text = asr_service.transcribe(file)
    return {'text': text[0]}
