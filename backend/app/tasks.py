# Celery tasks will be defined here
from app.celery_worker import celery


@celery.task
def sample_task(x: int, y: int):
    """Sample task for testing"""
    return x + y
