"""Optional Celery app for background work (e.g. batch generations, async analytics
rollups). Real and runnable, but NOT required for the core API — the app works
fully without a worker. Start one with:

    celery -A app.celery_app.celery worker --loglevel=info

It needs a broker; set REDIS_URL (Celery reuses it). If REDIS_URL is unset, this
module still imports cleanly and is simply never used."""
from celery import Celery

from .config import get_settings

settings = get_settings()

broker = settings.redis_url or "memory://"
backend = settings.redis_url or "cache+memory://"

celery = Celery("copilot", broker=broker, backend=backend)
celery.conf.update(task_serializer="json", result_serializer="json", accept_content=["json"])
