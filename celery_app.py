"""
Celery application entry point for local worker startup.
"""
import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

broker_url = os.getenv('CELERY_BROKER_URL') or os.getenv('REDIS_URL', 'redis://localhost:6379/0')
result_backend = os.getenv('CELERY_RESULT_BACKEND', broker_url)

celery = Celery('optc_farmbot', broker=broker_url, backend=result_backend)
celery.conf.update(task_ignore_result=True)
app = celery


@celery.task(name='optc_farmbot.ping')
def ping():
    return 'pong'
