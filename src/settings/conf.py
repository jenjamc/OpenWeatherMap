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

    DB_DRIVER: str = 'postgresql+asyncpg'
    DB_USER: str = 'postgres'
    DB_PASS: str = 'postgres123'
    DB_HOST: str = 'host.docker.internal'
    DB_PORT: int = 5432
    DB_NAME: str = 'src'

    SECRET_KEY: str = 'your-secret-key'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    RETELL_API_KEY: str = 'YOUR_RETELL_API_KEY'
    RETELL_WEBHOOK_KEY: str = 'YOUR_RETELL_API_KEY'
    RETELL_WEBHOOK: str = 'http://localhost:4000/users/webhook'

    DB_MONGO_NAME: str = 'company'
    DB_MONGO_HOST: str = 'mongo'
    DB_MONGO_PORT: int = 27017
    DB_MONGO_USERNAME: str = 'admin'
    DB_MONGO_PASSWORD: str = 'password'

    OPENWEATHER_API_KEY: str = '129d9ea5e37e0a0662aa602974d1fa07'
    OPENWEATHER_BASE_URL: AnyHttpUrl = AnyHttpUrl('https://api.openweathermap.org')
    REQUEST_TIMEOUT_SECONDS: float = 10.0

    CACHE_TTL_SECONDS: int = 300
    DATA_DIR: str = 'data'
    LOG_DB_PATH: str = 'data/weather_events.db'

    RATE_LIMIT_REQUESTS: int = 60
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    BASE_HTTP_CLIENT_TIMEOUT: int = 5

    @property
    def sqlalchemy_database_uri(self) -> str:
        return f'{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'  # noqa

    @property
    def db_mongo_uri(self):
        return f'mongodb://{settings.DB_MONGO_USERNAME}:{settings.DB_MONGO_PASSWORD}@{settings.DB_MONGO_HOST}:{settings.DB_MONGO_PORT}/?retryWrites=false'


settings = Settings()
