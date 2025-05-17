from app.pattern_repository.pattern_repository import BaseRepository
from app.models.task import Task
from sqlalchemy import select, insert, update
from app.backend.db_depends import AsyncSession
from app.schemas import CreateTask

class TaskRepository(BaseRepository):
    model = Task

    @classmethod
    async def create_task(cls, db: AsyncSession, createtask: CreateTask):
        await db.execute(insert(Task).values(
            title=createtask.title,
            description=createtask.description,
            status=createtask.status,
            user_id=createtask.user_id
        ))
        await db.commit()

    @classmethod
    async def update_by(cls, db: AsyncSession, update_task: CreateTask, task_id: int):
        await db.execute(update(Task).where(Task.user_id == task_id).values(
            title=update_task.title.capitalize(),
            description=update_task.description,
            status=update_task.status,
            user_id=update_task.user_id))
        await db.commit()

    @classmethod
    async def get_by_user_id(cls, db: AsyncSession, user_id: int):
        return await db.scalar(select(cls.model).where(cls.model.user_id == user_id))

    @classmethod
    async def get_by_title(cls, db: AsyncSession, title: str):
        return await db.scalar(select(cls.model).where(cls.model.title == title.capitalize()))

    @classmethod
    async def del_by_id(cls, db: AsyncSession, task_id: int):
        return await db.scalar(select(Task).where(Task.user_id == task_id))

    @classmethod
    async def del_by_title(cls, db: AsyncSession, title: str):
        return await db.scalar(select(Task).where(Task.title == title))
