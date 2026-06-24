"""Analytics: record every generation and aggregate it for the dashboard.

record() is called from each feature route. It writes an AnalyticsEvent row and
bumps lightweight Redis counters when Redis is present (fast reads without
scanning the table). summary() aggregates straight from the DB so it works with
or without Redis."""
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from . import models
from .config import get_settings

settings = get_settings()

_redis = None
if settings.redis_url:
    try:
        import redis  # type: ignore

        _redis = redis.from_url(settings.redis_url, decode_responses=True)
        _redis.ping()
    except Exception:
        _redis = None


def record(db: Session, user_id: int, mode: str, tone: str, latency_ms: int, cached: bool) -> None:
    event = models.AnalyticsEvent(
        user_id=user_id, mode=mode, tone=tone, latency_ms=latency_ms, cached=1 if cached else 0
    )
    db.add(event)
    db.commit()

    if _redis is not None:
        try:
            today = date.today().isoformat()
            _redis.hincrby("an:tone_counts", tone, 1)
            _redis.hincrby("an:mode_counts", mode, 1)
            _redis.incr(f"an:daily:{today}")
        except Exception:
            pass


def summary(db: Session, user_id: int | None = None) -> dict:
    q = db.query(models.AnalyticsEvent)
    if user_id is not None:
        q = q.filter(models.AnalyticsEvent.user_id == user_id)

    total = q.count()
    avg_latency = (
        db.query(func.avg(models.AnalyticsEvent.latency_ms))
        .filter(*( [models.AnalyticsEvent.user_id == user_id] if user_id else [] ))
        .scalar()
    ) or 0
    cache_hits = q.filter(models.AnalyticsEvent.cached == 1).count()

    tone_rows = (
        db.query(models.AnalyticsEvent.tone, func.count().label("c"))
        .filter(*( [models.AnalyticsEvent.user_id == user_id] if user_id else [] ))
        .group_by(models.AnalyticsEvent.tone)
        .order_by(func.count().desc())
        .limit(8)
        .all()
    )
    mode_rows = (
        db.query(models.AnalyticsEvent.mode, func.count().label("c"))
        .filter(*( [models.AnalyticsEvent.user_id == user_id] if user_id else [] ))
        .group_by(models.AnalyticsEvent.mode)
        .order_by(func.count().desc())
        .all()
    )

    # Requests per day for the last 7 days.
    since = datetime.now(timezone.utc) - timedelta(days=7)
    daily_rows = (
        db.query(
            func.date(models.AnalyticsEvent.created_at).label("d"),
            func.count().label("c"),
        )
        .filter(models.AnalyticsEvent.created_at >= since)
        .filter(*( [models.AnalyticsEvent.user_id == user_id] if user_id else [] ))
        .group_by(func.date(models.AnalyticsEvent.created_at))
        .all()
    )

    return {
        "total_requests": total,
        "avg_latency_ms": round(float(avg_latency), 1),
        "cache_hits": cache_hits,
        "most_used_tones": [{"tone": t, "count": c} for t, c in tone_rows],
        "by_module": [{"mode": m, "count": c} for m, c in mode_rows],
        "daily": [{"date": str(d), "count": c} for d, c in daily_rows],
        "cache_backend": _backend(),
    }


def _backend() -> str:
    return "redis" if _redis is not None else "memory"
