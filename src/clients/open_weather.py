from collections import defaultdict
from datetime import UTC
from datetime import datetime


from src.clients.http import BaseHTTPClient
from src.exceptions import ValidationError
from src.schemas.weather import WeatherRequestSchema, WeatherRequestForecastSchema
from src.settings.conf import settings
from src.settings.constants import ErrorMessages


class OpenWeatherClient(BaseHTTPClient):

    class ROUTES:
        API_KEY = settings.OPENWEATHER_API_KEY
        GET_FORECAST_BY_COORDINATES: str = 'data/2.5/forecast?q={city}&cnt={cnt}&appid=' + API_KEY


    async def get_forecast_by_coordinates(self, params: WeatherRequestForecastSchema):
        response = await self.get(url=self.ROUTES.GET_FORECAST_BY_COORDINATES.format(
            city=params.city,
            cnt=params.days_forecast,
        ))
        # return GeoCodesSchema(**response.json()[0])
        return response.json()

