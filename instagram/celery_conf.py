from celery import Celery
from datetime import timedelta
import os



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instagram.settings')

celery_app = Celery('instagram')
celery_app.autodiscover_tasks()

celery_app.broker_url = 'amqp://'
celery_app.result_backend = 'rpc://'
celery_app.task_serializer = 'json'
celery_app.conf.result_serializer = 'pickle'
celery_app.conf.accept_content = ['json', 'pickle']
celery_app.conf.result_expires = timedelta(days=1)
celery_app.conf.task_always_eager = False
celery_app.conf.worker_prefetch_multiplier = 4
