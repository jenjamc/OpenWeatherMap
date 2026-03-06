import asyncio
import os
from datetime import datetime
from datetime import timedelta

import ujson
from pydantic import TypeAdapter
from sqlalchemy import desc
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src import settings
from src.clients import open_weather_client
from src.models.weather import Weather
from src.schemas.weather import WeatherBatchResponseSchema
from src.schemas.weather import WeatherRequestSchema
from src.services.base import BaseService
from src.settings.db import async_session

SEMAPHORE = asyncio.Semaphore(5)


class WeatherService(BaseService[Weather]):
    MODEL = Weather

    async def get_weather(self, params: WeatherRequestSchema) -> list[WeatherBatchResponseSchema]:
        tasks = [self._get_city_weather(city, params.hours_forecast) for city in params.cities]

        results = await asyncio.gather(*tasks)
        return TypeAdapter(list[WeatherBatchResponseSchema]).validate_python(results)

    async def _get_city_weather(self, city: str, hours_forecast: int):
        async with SEMAPHORE:
            async with async_session() as session:  # type: ignore
                last_event = await self._get_last_weather(city, hours_forecast, session)
                if last_event is not None and self._is_cache_valid(last_event):
                    cached = await self._read_cache(last_event)
                    if cached:
                        return cached

                result = await self._fetch_weather_api(city, hours_forecast)

                await self._store_result(city, hours_forecast, result, session)

                return result

    @staticmethod
    def _is_cache_valid(event: Weather):
        return datetime.now() - event.created_at < timedelta(minutes=settings.CACHE_TTL_MINUTES)

    @staticmethod
    async def _read_cache(event: Weather):
        if not os.path.exists(event.file_path):
            return None

        with open(event.file_path, 'r') as f:
            return ujson.load(f)

    @staticmethod
    async def _fetch_weather_api(city: str, hours_forecast: int):
        return await open_weather_client.get_forecast_by_coordinates(city, hours_forecast)

    async def _store_result(self, city: str, hours_forecast: int, result: dict, session: AsyncSession):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        filename = f'{city}_{hours_forecast}_{timestamp}.json'
        file_path = f'{settings.DATA_DIR}/{filename}'

        with open(file_path, 'w') as f:
            ujson.dump(result, f, indent=2)

        event = Weather(
            city=city,
            file_path=file_path,
            hours_forecast=hours_forecast,
        )

        await self.insert_obj(session, event)

    async def _get_last_weather(self, city: str, hours_forecast: int, session: AsyncSession):
        query = (
            select(self.MODEL)
            .where(
                self.MODEL.city == city,
                self.MODEL.hours_forecast == hours_forecast,
            )
            .order_by(desc(self.MODEL.created_at))
            .limit(1)
        )

        result = await session.execute(query)
        return result.scalar_one_or_none()
