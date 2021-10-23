from deeprtc.modules.asr.service import ASRService
from deeprtc.celery import celery


asr_service = ASRService()


@celery.task()
def asr_predict_task(file_name: str, object_id):
    asr_service.transcribe(file_name, object_id)
    return True
