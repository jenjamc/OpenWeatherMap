from http import HTTPStatus
from typing import TYPE_CHECKING

from src import project_name
from src import version

if TYPE_CHECKING:
    from httpx import AsyncClient


async def test_health_ok(client: 'AsyncClient') -> None:
    response = await client.get('/health')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'db': True}


async def test_version(client: 'AsyncClient') -> None:
    response = await client.get('/info')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'version': version, 'project_name': project_name}
