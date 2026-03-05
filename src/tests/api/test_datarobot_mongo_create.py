from http import HTTPStatus

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.tests.factories import TenantFactory
from src.tests.factories import UserFactory

url = '/datarobot/mongo/create'


async def test_mongo_create(
        client: AsyncClient,
) -> None:
    request_data = {
        'name': 'company1',
    }
    response = await client.post(url, json=request_data)
    assert response.status_code == HTTPStatus.OK
    assert response.json()['name'] == 'company1'
    assert response.json()['state'] == 'IN_PROGRESS'
