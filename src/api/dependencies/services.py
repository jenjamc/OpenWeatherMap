from src.services.weather import WeatherService


async def get_weather_service() -> WeatherService:
    return WeatherService()
