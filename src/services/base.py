from typing import Generic
from typing import Sequence
from typing import Type
from typing import TypeVar

from sqlalchemy import Select
from sqlalchemy import exists
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Query

from src.models.base import Base

ModelT = TypeVar('ModelT', bound=Base)


class BaseService(Generic[ModelT]):
    MODEL: Type[ModelT] = Base

    async def fetch_one(self, session: AsyncSession, filters: Sequence):
        query = select(self.MODEL).where(*filters)
        return await session.scalar(query)

    async def insert(self, session: AsyncSession, values: dict) -> ModelT:
        obj = self.MODEL(**values)
        session.add(obj)
        await session.commit()
        return obj

    @staticmethod
    async def insert_obj(session: AsyncSession, obj: ModelT) -> ModelT:
        session.add(obj)
        await session.commit()
        return obj
