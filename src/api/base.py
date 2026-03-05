from http import HTTPStatus

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src import project_name
from src.api.dependencies.db import get_db_session
from src.schemas.base import HealthSchema
from src.schemas.base import ServiceInfoSchema

router = APIRouter()


@router.get(
    '/health',
    summary='Health check',
    status_code=HTTPStatus.OK,
    response_model=HealthSchema,
    responses={
        200: {'model': HealthSchema},
        500: {'model': HealthSchema},
    },
)
async def health(session: AsyncSession = Depends(get_db_session)) -> HealthSchema:
    await session.execute(select(1))  # type: ignore
    return HealthSchema(db=True)


@router.get(
    '/info',
    summary='API get info',
    response_model=ServiceInfoSchema,
)
async def get_service_info(request: Request) -> ServiceInfoSchema:
    return ServiceInfoSchema(version=request.app.version, project_name=project_name)
