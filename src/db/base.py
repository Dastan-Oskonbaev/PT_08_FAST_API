from typing import TypeVar, Generic, Type, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData, select, update, delete

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def get_one(self, id_: Any) -> Optional[T]:
        stmt = select(self.model).where(self.model.id == id_)
        res = await self.session.execute(stmt)
        return res.scalars().one_or_none()

    async def get_all(self) -> List[T]:
        stmt = select(self.model)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def create(self, **kwargs) -> T:
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def update(self, id_: Any, **kwargs) -> T:
        stmt = update(self.model).where(self.model.id == id_).values(**kwargs).returning(self.model.id)
        res = await self.session.execute(stmt)
        if not res.first():
            await self.session.rollback()
            return None
        await self.session.commit()
        return await self.get_one(id_)


    async def delete(self, id_: Any) -> bool:
        stmt = delete(self.model).where(self.model.id == id_)
        res = await self.session.execute(stmt)
        await self.session.commit()
        return (res.rowcount or 0) > 0


