"""
Minimal Celery application for local worker startup.
"""
import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

celery_app = Celery(
    'optc_farmbot',
    broker=redis_url,
    backend=redis_url,
)


@celery_app.task(name='optc_farmbot.healthcheck')
def healthcheck():
    """Simple task used to validate the local worker."""
    return 'ok'
