from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from src.settings.conf import settings

engine = create_async_engine(settings.sqlite_database_uri)
async_session = sessionmaker(None, expire_on_commit=False, class_=AsyncSession)
