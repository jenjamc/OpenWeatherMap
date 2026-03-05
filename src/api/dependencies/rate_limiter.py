from fastapi import HTTPException
from fastapi import Request
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

from src.settings.redis import redis


class RateLimiter:
    def __init__(self, seconds: int):
        self.seconds = seconds

    async def __call__(
        self,
        request: Request,
    ) -> None:
        client_host = request.client.host if request.client is not None else 'unknown'
        key = f"{request.scope['path']}/{client_host}"
        rate = await redis.get(key)
        if rate:
            retry_after = await redis.ttl(key)
            raise HTTPException(
                HTTP_429_TOO_MANY_REQUESTS,
                detail='Too Many Requests',
                headers={'Retry-After': str(retry_after)},
            )
        await redis.setex(key, self.seconds, 1)
