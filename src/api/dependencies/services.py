from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.db import get_db_session
from src.services.weather import WeatherService


async def get_weather_service(session: AsyncSession = Depends(get_db_session)) -> WeatherService:
    return WeatherService(session)
