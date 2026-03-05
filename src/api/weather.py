from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query

from src import settings
from src.api.dependencies.rate_limiter import RateLimiter
from src.api.dependencies.services import get_weather_service
from src.schemas.weather import WeatherBatchResponseSchema
from src.schemas.weather import WeatherRequestSchema
from src.services.weather import WeatherService

router = APIRouter()


@router.get(
    '/get-by-cities',
    summary='Fetch weather for one or more cities',
    description='Returns current weather up to 5 forecast_days with 3 hour intervals.',
    response_model=list[WeatherBatchResponseSchema],
    dependencies=[Depends(RateLimiter(settings.RATE_LIMIT_REQUESTS))],
)
async def get_weather(
    params: Annotated[WeatherRequestSchema, Query()],
    weather_service: WeatherService = Depends(get_weather_service),
) -> list[WeatherBatchResponseSchema]:
    return await weather_service.get_weather(params)
