"""
Celery tasks for background farming automation.
"""
import os

from celery import Celery

celery_app = Celery(
    'optc_farmbot',
    broker=os.getenv('CELERY_BROKER_URL', os.getenv('REDIS_URL', 'memory://')),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'cache+memory://'),
)
celery_app.conf.update(
    task_always_eager=False,
    task_store_eager_result=True,
)


def configure_celery(app):
    celery_app.conf.update(
        broker_url=app.config.get('CELERY_BROKER_URL', celery_app.conf.broker_url),
        result_backend=app.config.get('CELERY_RESULT_BACKEND', celery_app.conf.result_backend),
        task_always_eager=app.config.get('CELERY_TASK_ALWAYS_EAGER', celery_app.conf.task_always_eager),
        task_store_eager_result=True,
    )


@celery_app.task(name='optc_farmbot.execute_farm_session')
def execute_farm_session_task(session_id):
    from app import create_app
    from bot.services import execute_farm_session

    app = create_app()
    with app.app_context():
        return execute_farm_session(session_id)


def enqueue_farm_session(session_id, force_sync=False):
    if force_sync or celery_app.conf.task_always_eager:
        from bot.services import execute_farm_session

        return None, execute_farm_session(session_id)

    async_result = execute_farm_session_task.delay(session_id)
    return async_result.id, None
