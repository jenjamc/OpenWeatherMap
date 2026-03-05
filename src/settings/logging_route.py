import logging
import uuid
from contextvars import ContextVar
from json import JSONDecodeError
from typing import Callable

import ujson
from fastapi.routing import APIRoute
from fastapi.routing import Request
from fastapi.routing import Response

logger = logging.getLogger(__name__)


class LoggingRoute(APIRoute):
    @classmethod
    async def get_request_data(cls, request: Request) -> dict:
        body = await cls.get_request_body(request)
        return {
            'url': request.url.path,
            'method': request.method,
            'json': body,
        }

    @classmethod
    def get_error_response_data(cls, request: Request, error: Exception) -> dict:
        data = cls.get_response_data(request)
        data['error'] = str(error)
        return data

    @staticmethod
    async def get_request_body(request: Request) -> dict:
        try:
            return await request.json() or {}
        except JSONDecodeError:
            return {}
        except UnicodeDecodeError:
            return dict(await request.form())

    @staticmethod
    def get_response_data(request: Request, response: Response | None = None) -> dict:
        response_data = {
            'url': request.url.path,
            'method': request.method,
            'json': ujson.loads(response.body.decode()) if response else None,  # type: ignore
        }

        if response:
            response_data['status_code'] = str(response.status_code)

        return response_data

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            logger.info(
                {
                    'message': 'Incoming request',
                    'json': await self.get_request_data(request),
                }
            )
            try:
                response = await original_route_handler(request)
                logger.info(
                    {
                        'message': 'Outgoing response',
                        **self.get_response_data(request, response),
                    }
                )
            except Exception as err:
                logger.info(
                    {
                        'message': f'External response from {request.url}',
                        **self.get_error_response_data(request, err),
                    }
                )
                raise err
            return response

        return custom_route_handler
