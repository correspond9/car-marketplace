import redis.asyncio as redis

from app.core.config import settings

_redis_client: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


async def close_redis() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None


class RateLimiter:
    def __init__(self, redis_client: redis.Redis, key_prefix: str, limit: int, window_seconds: int):
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.limit = limit
        self.window_seconds = window_seconds

    async def is_allowed(self, identifier: str) -> bool:
        key = f"{self.key_prefix}:{identifier}"
        count = await self.redis.incr(key)
        if count == 1:
            await self.redis.expire(key, self.window_seconds)
        return count <= self.limit
