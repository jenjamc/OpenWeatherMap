from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.settings.conf import Settings


def init_middlewares(app: FastAPI, app_settings: Settings):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
