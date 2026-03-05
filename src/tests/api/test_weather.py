from http import HTTPStatus

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


url = '/weather'


async def test_sql(
        client: AsyncClient,
        session: AsyncSession,
) -> None:
    tenant = TenantFactory()
    user = UserFactory(tenant=tenant)
    response = await client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert user
    assert response.json() == {'db': True}
