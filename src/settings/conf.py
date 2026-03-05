from enum import Enum

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


class Env(str, Enum):
    TESTING = 'TESTING'
    LOCAL = 'LOCAL'
    DEV = 'DEV'
    STAGING = 'STAGING'
    PRODUCTION = 'PRODUCTION'


class LogLevel(str, Enum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'


class Settings(BaseSettings):
    PORT: int = 4000
    ENV: Env = Env.PRODUCTION
    DEBUG: bool = False
    LOG_LEVEL: str = LogLevel.INFO
    ALLOWED_ORIGINS: str = 'http://localhost'

    DB_DRIVER: str = 'sqlite+aiosqlite'
    DB_DRIVER_SYNC: str = 'sqlite'
    DB_NAME: str = 'open_weather.db'

    OPENWEATHER_API_KEY: str = 'api_key'
    OPENWEATHER_BASE_URL: AnyHttpUrl = AnyHttpUrl('https://api.openweathermap.org')
    REQUEST_TIMEOUT_SECONDS: float = 10.0

    CACHE_TTL_SECONDS: int = 300
    DATA_DIR: str = 'data'
    LOG_DB_PATH: str = 'data/weather_events.db'

    RATE_LIMIT_REQUESTS: int = 5
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    BASE_HTTP_CLIENT_TIMEOUT: int = 5
    CACHE_TTL_MINUTES: int = 5

    REDIS_URL: str = 'redis://redis:6379'

    @property
    def sqlite_database_uri(self) -> str:
        return f'{self.DB_DRIVER}:///{self.DATA_DIR}/{self.DB_NAME}'  # noqa

    @property
    def sqlite_database_uri_sync(self) -> str:
        return f'{self.DB_DRIVER_SYNC}:///{self.DATA_DIR}/{self.DB_NAME}'  # noqa


settings = Settings()
