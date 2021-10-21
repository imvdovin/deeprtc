from datetime import datetime
from io import BytesIO
from fastapi import APIRouter, File, UploadFile, BackgroundTasks
from fastapi.exceptions import HTTPException
from fastapi.responses import Response
from fastapi.param_functions import Depends
from deeprtc.modules.asr.service import ASRService
from deeprtc.modules.file.dto.update_audio_text_token_dto import UpdateAudioTextTokenDto
from deeprtc.modules.file.service import FileService
from deeprtc.modules.file.repository import FileRepository
from deeprtc.modules.file.dto.audio_text_token_dto import AudioTextTokenDto
from deeprtc.modules.file.dto.update_content_dto import UpdateFileTextContentDto
from bson import ObjectId


router = APIRouter(tags=['files'])


@router.post('/')
async def post_audio(
        background_tasks: BackgroundTasks,
        audio_file: UploadFile = File(...),
        asr_service: ASRService = Depends(ASRService),
        file_service: FileService = Depends(FileService)):
    save_result = await file_service.save(audio_file)
    insert_result = await file_service.create_token_for_transcribed_audio(save_result.name)
    background_tasks.add_task(
        asr_service.transcribe, save_result.path, insert_result.inserted_id)
    return {'id': str(insert_result.inserted_id)}


@router.get('/word')
async def export_ms_word(
        token: str = '',
        file_service: FileService = Depends(FileService)):
    if token == '':
        raise HTTPException(status_code=400, detail='Text is empty')

    doc_stream: BytesIO = await file_service.create_word_by_text(
        token)

    rounded_timestamp = round(datetime.utcnow().timestamp())

    filename = f'transcribed_{rounded_timestamp}.docx'

    return Response(
        doc_stream.getvalue(),
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        headers={'Content-Disposition': f'inline; filename="{filename}"'})


@router.get('/poll-token/{object_id}')
async def poll_token(object_id, file_repository: FileRepository = Depends(FileRepository)):
    token: AudioTextTokenDto = await file_repository.find_one(object_id)

    token['_id'] = str(token['_id'])

    return token


@router.put('/{object_id}/content')
async def update_file_content(
        object_id,
        update_dto: UpdateFileTextContentDto,
        file_repository: FileRepository = Depends(FileRepository)):
    update_token_dto = UpdateAudioTextTokenDto(text=update_dto.text)
    res = await file_repository.update(
        {'_id': ObjectId(object_id)}, update_token_dto)

    return {'id': res.upserted_id}
