"""Per-user daily rate limit. Redis-backed when REDIS_URL is set (survives restarts
and works across processes); in-memory otherwise. One function, one seam."""
from collections import defaultdict
from datetime import date

from fastapi import HTTPException, status

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

_mem: dict[int, dict[str, int]] = defaultdict(dict)


def enforce(user_id: int) -> int:
    """Increment today's count, raise 429 if over limit, return remaining."""
    today = date.today().isoformat()
    limit = settings.rate_limit_per_day

    if _redis is not None:
        try:
            key = f"rl:{user_id}:{today}"
            used = _redis.incr(key)
            if used == 1:
                _redis.expire(key, 60 * 60 * 26)
            if used > limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Daily limit of {limit} requests reached.",
                )
            return limit - used
        except HTTPException:
            raise
        except Exception:
            pass  # fall through to memory

    used = _mem[user_id].get(today, 0)
    if used >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily limit of {limit} requests reached.",
        )
    _mem[user_id][today] = used + 1
    return limit - (used + 1)
