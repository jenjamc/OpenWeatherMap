from src.clients.open_weather import OpenWeatherHTTPClient
from src.settings.conf import settings

open_weather_client = OpenWeatherHTTPClient(settings.OPENWEATHER_BASE_URL)
