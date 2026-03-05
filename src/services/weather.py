from datetime import UTC
from datetime import datetime
from pathlib import Path

from src.clients import open_weather_client
from src.clients.open_weather import OpenWeatherClient
from src.models.weather import Weather
from src.schemas.weather import WeatherResultSchema, WeatherRequestSchema, WeatherRequestForecastSchema
from src.services.base import BaseService


class WeatherService(BaseService[Weather]):
    MODEL = Weather

    async def get_weather(self, params: WeatherRequestSchema):
        city_weather = WeatherRequestForecastSchema(city=params.cities[0], days_forecast=params.days_forecast)
        return await open_weather_client.get_forecast_by_coordinates(city_weather)
