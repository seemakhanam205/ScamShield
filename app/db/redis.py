# app/db/redis.py
import os
from typing import AsyncGenerator
import redis.asyncio as aioredis
from app.core.config import settings

REDIS_URL = os.getenv("REDIS_URL", settings.REDIS_URL)

# Redis Async Client
redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    """Dependency injection for Redis client."""
    yield redis_client