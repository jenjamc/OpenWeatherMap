import uvicorn

from src.app import create_app
from src.settings.conf import settings
from src.settings.logging import LOG_CONFIG

app = create_app()

if __name__ == '__main__':
    uvicorn_app = 'server:app' if settings.DEBUG else app
    uvicorn.run(
        app=uvicorn_app,
        host='0.0.0.0',  # noqa S104
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
        log_config=LOG_CONFIG,
        loop='uvloop',
        reload=settings.DEBUG,
    )
