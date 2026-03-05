import asyncio
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.api.dependencies.db import get_db_session
from src.api.dependencies.services import get_weather_service
from src.schemas.weather import WeatherErrorSchema, WeatherRequestSchema
from src.schemas.weather import WeatherResponseSchema
from src.services.weather import WeatherService

router = APIRouter()


@router.get(
    '/weather',
    summary='Fetch weather for one or more cities',
    description='Returns current weather (`forecast_days=1`) or a 3-day forecast (`forecast_days=3`).',
    # response_model=WeatherResponseSchema,
)
async def get_weather(
    params: Annotated[WeatherRequestSchema, Query()],
    weather_service: WeatherService = Depends(get_weather_service),
):
    return await weather_service.get_weather(params)