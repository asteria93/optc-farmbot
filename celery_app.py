import os

try:
    from celery import Celery
except ImportError:  # pragma: no cover - fallback for environments without Celery
    Celery = None


celery = Celery('optc_farmbot') if Celery else None


def configure_celery(app):
    if not celery:
        return None

    celery.conf.update(
        broker_url=app.config.get('CELERY_BROKER_URL', os.getenv('REDIS_URL', 'redis://localhost:6379/0')),
        result_backend=app.config.get('CELERY_RESULT_BACKEND', os.getenv('REDIS_URL', 'redis://localhost:6379/0')),
        task_ignore_result=False,
        task_serializer='json',
        result_serializer='json',
        accept_content=['json'],
        task_always_eager=app.config.get('CELERY_TASK_ALWAYS_EAGER', False),
    )

    class FlaskTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = FlaskTask
    return celery
