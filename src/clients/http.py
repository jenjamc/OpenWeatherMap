import logging
from http import HTTPStatus
from typing import Type
from urllib.parse import urljoin

import httpx
from pydantic import HttpUrl

from src import settings
from src.exceptions import HTTPClientError

logger = logging.getLogger(__name__)


class BaseHTTPClient:
    EXC_CLASS: Type[HTTPClientError] = HTTPClientError

    def __init__(self, base_url: HttpUrl, timeout: float = settings.BASE_HTTP_CLIENT_TIMEOUT):
        self.base_url = str(base_url)
        self.timeout = timeout

    def get_url(self, url: str) -> str:
        return urljoin(self.base_url, url)

    async def get(self, url: str, **kwargs) -> httpx.Response:
        return await self._request('GET', url, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        return await self._request('POST', url, **kwargs)

    async def patch(self, url: str, **kwargs) -> httpx.Response:
        return await self._request('PATCH', url, **kwargs)

    async def put(self, url: str, **kwargs) -> httpx.Response:
        return await self._request('PUT', url, **kwargs)

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        url = self.get_url(url)
        self._before_request_log(url, method, **kwargs)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(method, url, **kwargs)
        except httpx.HTTPError as err:
            logger.exception({'message': str(err)})
            raise self.EXC_CLASS(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, response_text=str(err), url=url)

        self._after_response_log(url=url, status_code=response.status_code, text=response.text)
        self._check_response(response)
        return response

    @staticmethod
    def _before_request_log(url: str, method: str, **kwargs) -> None:
        logger.info(
            {
                'message': f'External {method} request to {url}',
                'json': kwargs.get('json', {}),
                'data': kwargs.get('data', {}),
                'params': kwargs.get('params', {}),
            }
        )

    @staticmethod
    def _after_response_log(url: str, status_code: int, text: str) -> None:
        logger.info({'message': f'Received response from {url} with status code {status_code}', 'text': text})

    def _check_response(self, response: httpx.Response) -> None:
        if response.is_error:
            raise self.EXC_CLASS(status_code=response.status_code, response_text=response.text, url=str(response.url))
