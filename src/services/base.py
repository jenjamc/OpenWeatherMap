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

    def __init__(self, session: AsyncSession):
        self.session = session

    async def fetch_one(self, filters: Sequence, options: Sequence = ()) -> ModelT | None:
        query = select(self.MODEL).where(*filters).options(*options).limit(1)
        return await self.session.scalar(query)

    async def fetch_all(self, query: Query | Select) -> Sequence[ModelT]:
        return (await self.session.scalars(query)).all()

    async def update(self, filters: Sequence, values: dict) -> None:
        query = update(self.MODEL).where(*filters).values(**values).execution_options(synchronize_session='fetch')
        await self.session.execute(query)
        await self.session.commit()

    async def update_obj(self, obj: ModelT, values: dict) -> ModelT:
        await self.update(filters=(self.MODEL.id == obj.id,), values=values)
        obj.__dict__.update(values)
        await self.session.commit()
        return obj

    async def insert(self, values: dict) -> ModelT:
        obj = self.MODEL(**values)
        self.session.add(obj)
        await self.session.commit()
        return obj

    async def insert_obj(self, obj: ModelT) -> ModelT:
        self.session.add(obj)
        await self.session.commit()
        return obj

    async def exist(self, filters: Sequence) -> bool:
        query = exists(self.MODEL).where(*filters).select()
        return bool(await self.session.scalar(query))
