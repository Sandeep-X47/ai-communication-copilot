"""Cache for identical generation requests. Uses Redis when REDIS_URL is set,
otherwise a bounded in-memory dict. The rest of the app calls get()/set() and
never learns which backend answered — that's the whole point of the seam.

Same input + same parameters => cached result => no LLM call => no cost."""
import json

from .config import get_settings

settings = get_settings()

_redis = None
if settings.redis_url:
    try:
        import redis  # type: ignore

        _redis = redis.from_url(settings.redis_url, decode_responses=True)
        _redis.ping()
    except Exception:
        _redis = None  # fall back to memory if Redis is unreachable

_mem: dict[str, str] = {}
_MEM_MAX = 1000
_TTL = 60 * 60 * 24  # 1 day


def _key(parts: list[str]) -> str:
    return "cache:" + "|".join(parts)


def get(parts: list[str]) -> str | None:
    key = _key(parts)
    if _redis is not None:
        try:
            return _redis.get(key)
        except Exception:
            pass
    return _mem.get(key)


def set(parts: list[str], value: str) -> None:
    key = _key(parts)
    if _redis is not None:
        try:
            _redis.setex(key, _TTL, value)
            return
        except Exception:
            pass
    if len(_mem) >= _MEM_MAX:
        _mem.clear()
    _mem[key] = value


def backend_name() -> str:
    return "redis" if _redis is not None else "memory"
