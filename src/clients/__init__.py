from typing import cast

from pydantic import HttpUrl

from src.clients.open_weather import OpenWeatherHTTPClient
from src.settings.conf import settings

open_weather_client = OpenWeatherHTTPClient(cast(HttpUrl, settings.OPENWEATHER_BASE_URL))
