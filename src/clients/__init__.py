from src.clients.open_weather import OpenWeatherClient
from src.settings.conf import settings

open_weather_client = OpenWeatherClient(settings.OPENWEATHER_BASE_URL)
