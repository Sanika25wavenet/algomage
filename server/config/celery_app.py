# import eventlet
# eventlet.monkey_patch()

from celery import Celery
from config.settings import settings

# Initialize Celery
# Broker: Where tasks are sent (Redis)
# Backend: Where results are stored (Redis)
celery_app = Celery(
    "event_photo_system",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["jobs.tasks"] # Auto-load tasks from this module
)

# Optional: Configure default queue options
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

if __name__ == "__main__":
    celery_app.start()
