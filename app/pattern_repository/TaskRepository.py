from sqlalchemy import insert, select, update

from app.backend.db_depends import AsyncSession
from app.models.task import Task
from app.pattern_repository.BaseRepository import BaseRepository
from app.schemas import CreateTask


class TaskRepository(BaseRepository):
    """Класс для роута Task, в котором реализованы
    все специфичные методы только для работы с БД,
    наследник базового репозитория"""

    model = Task

    @classmethod
    async def create_task(cls, db: AsyncSession, createtask: CreateTask):
        """Метод для создания задачи"""

        await db.execute(
            insert(Task).values(
                title=createtask.title,
                description=createtask.description,
                status=createtask.status,
                user_id=createtask.user_id,
            )
        )
        await db.commit()

    @classmethod
    async def update_by(
        cls, db: AsyncSession, update_task: CreateTask, task_id: int
    ):
        """Метод для обновления задачи"""

        await db.execute(
            update(Task)
            .where(Task.user_id == task_id)
            .values(
                title=update_task.title.capitalize(),
                description=update_task.description,
                status=update_task.status,
                user_id=update_task.user_id,
            )
        )
        await db.commit()

    @classmethod
    async def get_by_user_id(cls, db: AsyncSession, user_id: int):
        """Метод для получения задачи через ее user_id"""

        return await db.scalar(
            select(cls.model).where(cls.model.user_id == user_id)
        )

    @classmethod
    async def get_by_title(cls, db: AsyncSession, title: str):
        """Метод для получения задачи через ее название"""

        return await db.scalar(
            select(cls.model).where(cls.model.title == title.capitalize())
        )

    @classmethod
    async def del_by_id(cls, db: AsyncSession, task_id: int):
        """Метод для удаления задачи через ее user_id"""

        return await db.scalar(select(Task).where(Task.user_id == task_id))

    @classmethod
    async def del_by_title(cls, db: AsyncSession, title: str):
        """Метод для удаления задачи через ее название"""

        return await db.scalar(select(Task).where(Task.title == title))

    @classmethod
    async def get_users_tasks(cls, db: AsyncSession, username_id: int):
        """Метод для получения всех товаров текущего пользователя"""

        values_tasks = await db.scalars(
            select(Task).where(Task.user_id == username_id)
        )
        return values_tasks.all()

    @classmethod
    async def get_free_tasks(cls, db: AsyncSession):
        """Метод для получения всех задач, которые не имеют владельца"""

        values = await db.scalars(select(Task).where(Task.user_id.is_(None)))
        return values.all()
