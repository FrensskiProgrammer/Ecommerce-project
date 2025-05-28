from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    """Базовый репозиторий, который содержит в себе все общие методы для роутов User и Task"""

    model = None

    @classmethod
    async def get_all(cls, db: AsyncSession):
        """Метод для получения всех записей с БД, общий для всех моделей"""

        value = await db.scalars(select(cls.model))
        return value.all()
