# mypy: ignore-errors
import asyncio
import time
from typing import AsyncGenerator
from typing import Generator

import pytest
import sqlalchemy as sa
from beanie import init_beanie
from fastapi import FastAPI
from httpx import ASGITransport
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from src.app import create_app
from src.models import Base
from src.models import metadata
from src.mongo_models import DOCUMENT_MODELS
from src.settings.conf import Env
from src.settings.conf import Settings
from src.settings.conf import settings
from src.settings.db import async_session
from src.tests.factories import FACTORIES


async def _create_test_db(engine: AsyncEngine, new_db_name: str):
    async with engine.connect() as conn:
        conn = await conn.execution_options(isolation_level='AUTOCOMMIT')
        await conn.execute(sa.text('DROP DATABASE IF EXISTS %s' % new_db_name))
        await conn.execute(sa.text('CREATE DATABASE %s' % new_db_name))


async def _drop_test_db(engine: AsyncEngine, new_db_name: str):
    async with engine.connect() as conn:
        conn = await conn.execution_options(isolation_level='AUTOCOMMIT')
        await conn.execute(
            sa.text(
                f'SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname'
                f" = '{new_db_name}' AND pid <> pg_backend_pid();"  # noqa: E231, E702
            )
        )
        await conn.execute(sa.text('DROP DATABASE %s' % new_db_name))


@pytest.fixture(scope='session')
def test_db_name() -> str:
    return f'src_tests_{int(time.time())}'


@pytest.fixture(scope='session')
def test_settings(test_db_name: str):
    return Settings(DB_NAME=test_db_name, ENV=Env.TESTING)


@pytest.fixture(scope='session', autouse=True)
async def init_test_db(
    test_settings: Settings,
    test_db_name: str,
) -> AsyncGenerator[None, None]:
    conn_url = settings.sqlalchemy_database_uri
    engine = create_async_engine(conn_url, poolclass=NullPool)
    await _create_test_db(engine, test_db_name)
    test_engine = create_async_engine(test_settings.sqlalchemy_database_uri, poolclass=NullPool)
    async with test_engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    yield

    await test_engine.dispose()
    await _drop_test_db(engine, test_db_name)
    await engine.dispose()


@pytest.fixture(scope='function')
async def app(
        test_settings: Settings,
        mongo_client: AsyncIOMotorClient,
        test_mongo_db_name: str,
) -> FastAPI:
    db = mongo_client[test_mongo_db_name]
    await init_beanie(database=db, document_models=DOCUMENT_MODELS)   # type: ignore
    fastapi_app = create_app(test_settings)
    return fastapi_app


@pytest.fixture(scope='function')
async def session(app: FastAPI) -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        for factory_ in FACTORIES:
            factory_._meta.sqlalchemy_session = session

        yield session


@pytest.fixture(scope='function', autouse=True)
async def clear_db(session: AsyncSession) -> AsyncGenerator[None, None]:
    yield

    await session.execute(
        sa.text('TRUNCATE {};'.format(','.join(table.name for table in Base.metadata.tables.values())))
    )
    await session.commit()


@pytest.fixture(scope='function')
def test_mongo_db_name() -> str:
    return f'test_mongo_db_{int(time.time())}'


@pytest.fixture(scope='function')
async def mongo_client(
        test_settings: Settings,
        event_loop: asyncio.AbstractEventLoop,
) -> AsyncGenerator[AsyncIOMotorClient, None]:
    client: AsyncIOMotorClient = AsyncIOMotorClient(test_settings.db_mongo_uri)
    yield client

    for model in DOCUMENT_MODELS:
        await model.delete_all()


@pytest.fixture(scope='function')
def event_loop() -> Generator[asyncio.AbstractEventLoop, None]:
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope='function')
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test/users/') as client:
        yield client


@pytest.fixture
def non_mocked_hosts() -> list:
    return ['test']
