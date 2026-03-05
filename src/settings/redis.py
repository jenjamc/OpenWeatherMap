from redis import asyncio as aioredis

from src import settings

redis = aioredis.from_url(settings.REDIS_URL, encoding='utf8', decode_responses=True, max_connections=30)
