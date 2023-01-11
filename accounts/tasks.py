from celery import shared_task
from .models import Story
from datetime import datetime, timedelta
import pytz



@shared_task
def remove_expired_stories():
    expired_time = datetime.now(tz=pytz.timezone('Asia/Tehran')) - timedelta(seconds=30) #####
    Story.objects.filter(created__lt=expired_time).delete()

