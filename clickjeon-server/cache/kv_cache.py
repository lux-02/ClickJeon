import json
import os

from upstash_redis import Redis

_redis: Redis | None = None


def _get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis(
            url=os.environ["UPSTASH_REDIS_REST_URL"],
            token=os.environ["UPSTASH_REDIS_REST_TOKEN"],
        )
    return _redis


def cache_get(key: str) -> dict | None:
    try:
        value = _get_redis().get(key)
        return json.loads(value) if value else None
    except Exception:
        return None


def cache_set(key: str, value: dict, ttl_seconds: int) -> None:
    try:
        _get_redis().setex(key, ttl_seconds, json.dumps(value))
    except Exception:
        pass
