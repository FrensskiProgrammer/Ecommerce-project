from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class BaseRepository:

    model = None

    @classmethod
    async def get_all(cls, db: AsyncSession):
        value = await db.scalars(select(cls.model))
        return value.all()
