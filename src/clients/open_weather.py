from src.clients.http import BaseHTTPClient
from src.exceptions import HTTPClientError
from src.exceptions import ValidationError
from src.settings.conf import settings
from src.settings.constants import ErrorMessages


class OpenWeatherHTTPClient(BaseHTTPClient):
    class ROUTES:
        API_KEY = settings.OPENWEATHER_API_KEY
        GET_FORECAST_BY_CITY: str = 'data/2.5/forecast?q={city}&cnt={cnt}&appid=' + API_KEY

    async def get_forecast_by_coordinates(self, city: str, hours_forecast: int):
        try:
            response = await self.get(
                url=self.ROUTES.GET_FORECAST_BY_CITY.format(
                    city=city,
                    cnt=hours_forecast,
                )
            )
            return response.json()
        except HTTPClientError:
            raise ValidationError(ErrorMessages.INVALID_CITY.format(city))
