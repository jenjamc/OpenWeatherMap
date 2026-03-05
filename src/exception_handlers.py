import logging
from http import HTTPStatus

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
from fastapi.responses import Response

from src.exceptions import AuthError
from src.exceptions import DoesNotExistError
from src.exceptions import ForbiddenError
from src.exceptions import HTTPClientError
from src.exceptions import ValidationError

logger = logging.getLogger(__name__)


class FastAPIExceptionHandlers:
    def __init__(self, app: FastAPI):
        self.app = app
        self.register_handlers()

    def register_handlers(self):
        self.app.exception_handler(HTTPClientError)(self.http_client_exception_handler)
        self.app.exception_handler(DoesNotExistError)(self.does_not_exist_exception_handler)
        self.app.exception_handler(ValidationError)(self.validation_exception_handler)
        self.app.exception_handler(ForbiddenError)(self.forbidden_exception_handler)
        self.app.exception_handler(AuthError)(self.auth_exception_handler)

    @staticmethod
    async def http_client_exception_handler(request: Request, exc: HTTPClientError) -> Response:
        logger.error({'message': str(exc)})
        return JSONResponse(
            status_code=HTTPStatus.BAD_GATEWAY,
            content=HTTPStatus.BAD_GATEWAY.phrase,
        )

    @staticmethod
    async def does_not_exist_exception_handler(request: Request, exc: DoesNotExistError) -> Response:
        return await http_exception_handler(
            request=request,
            exc=HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(exc)),
        )

    @staticmethod
    async def forbidden_exception_handler(request: Request, exc: ForbiddenError) -> Response:
        return await http_exception_handler(
            request=request,
            exc=HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=str(exc)),
        )

    @staticmethod
    async def auth_exception_handler(request: Request, exc: AuthError) -> Response:
        return await http_exception_handler(
            request=request,
            exc=HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=str(exc)),
        )

    @staticmethod
    async def validation_exception_handler(request: Request, exc: ValidationError) -> Response:
        return await http_exception_handler(
            request=request,
            exc=HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(exc)),
        )
