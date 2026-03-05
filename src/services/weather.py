import asyncio
import os
from datetime import UTC, timedelta
from datetime import datetime
from pathlib import Path

import ujson
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src import settings
from src.clients import open_weather_client
from src.clients.open_weather import OpenWeatherClient
from src.models.weather import Weather
from src.schemas.weather import WeatherResultSchema, WeatherRequestSchema, WeatherRequestForecastSchema
from src.services.base import BaseService
from src.settings.db import async_session

SEMAPHORE = asyncio.Semaphore(5)

class WeatherService(BaseService[Weather]):
    MODEL = Weather

    async def get_weather(self, params: WeatherRequestSchema):
        tasks = [
            self._get_city_weather(city, params.days_forecast)
            for city in params.cities
        ]

        results = await asyncio.gather(*tasks)
        return results

    async def _get_city_weather(self, city: str, days_forecast: int):
        async with SEMAPHORE:
            async with async_session() as session:

                last_event = await self._get_last_weather(city, session)
                if last_event is not None and self._is_cache_valid(last_event):
                    cached = await self._read_cache(last_event)
                    if cached:
                        return cached

                result = await self._fetch_weather_api(city, days_forecast)

                await self._store_result(city, result, session)

                return result

    @staticmethod
    def _is_cache_valid(event: Weather):
        return datetime.now() - event.created_at < timedelta(
            minutes=settings.CACHE_TTL_MINUTES
        )

    @staticmethod
    async def _read_cache(event: Weather):
        if not os.path.exists(event.file_path):
            return None

        with open(event.file_path, 'r') as f:
            return ujson.load(f)

    @staticmethod
    async def _fetch_weather_api(city: str, days_forecast: int):
        request = WeatherRequestForecastSchema(
            city=city,
            days_forecast=days_forecast,
        )

        return await open_weather_client.get_forecast_by_coordinates(
            request
        )


    async def _store_result(self, city: str, result: dict, session: AsyncSession):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        filename = f'{city}_{timestamp}.json'
        file_path = f'{settings.DATA_DIR}/{filename}'

        with open(file_path, 'w') as f:
            ujson.dump(result, f, indent=2)

        event = Weather(
            city=city,
            file_path=file_path,
        )

        await self.insert_obj(session, event)

    async def _get_last_weather(self, city: str, session: AsyncSession):
        stmt = (
            select(self.MODEL)
            .where(self.MODEL.city == city)
            .order_by(desc(self.MODEL.created_at))
            .limit(1)
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()
