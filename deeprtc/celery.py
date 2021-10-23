from celery import Celery


CELERY_IMPORTS = ('deeprtc.tasks',)


celery = Celery(include=['deeprtc.tasks'])
celery.conf.broker_url = "redis://localhost:6379"
celery.conf.result_backend = "redis://localhost:6379"
