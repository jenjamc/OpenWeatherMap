from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine

from src import version
from src.api import base
from src.api import weather
from src.exception_handlers import FastAPIExceptionHandlers
from src.middlewares import init_middlewares
from src.models import metadata
from src.settings.conf import Env
from src.settings.conf import Settings
from src.settings.conf import settings
from src.settings.db import async_session

PREFIX: str = '/weather'


def init_routes(fast_api_app: 'FastAPI') -> None:
    fast_api_app.include_router(base.router, prefix=PREFIX, tags=['Base'])
    fast_api_app.include_router(weather.router, prefix=PREFIX, tags=['Weather'])


def init_db(app_settings: Settings):
    engine = create_async_engine(app_settings.sqlite_database_uri)
    async_session.configure(bind=engine)
    metadata.bind = engine  # type: ignore


def create_app(app_settings: Settings = settings) -> FastAPI:
    app_settings = app_settings if app_settings is not None else settings
    is_production = app_settings.ENV == Env.PRODUCTION
    fast_api_app = FastAPI(
        title='Stobox4 User manager API',
        debug=app_settings.DEBUG,
        docs_url=None if is_production else f'{PREFIX}/docs',
        redoc_url=None if is_production else f'{PREFIX}/redoc',
        openapi_url=None if is_production else f'{PREFIX}/openapi.json',
        version=version,
    )
    init_middlewares(fast_api_app, app_settings)
    FastAPIExceptionHandlers(fast_api_app)
    init_db(app_settings)
    init_routes(fast_api_app)
    return fast_api_app
