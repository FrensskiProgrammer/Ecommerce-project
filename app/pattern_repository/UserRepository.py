from app.pattern_repository.BaseRepository import BaseRepository
from app.models.user import User
from app.models.task import Task
from sqlalchemy import select, insert, update
from app.backend.db import AsyncSession
from fastapi import HTTPException, status
from app.schemas import CreateUser
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class UserRepository(BaseRepository):

    model = User

    @classmethod
    async def get_free_users(cls, db: AsyncSession):
        lists_user_id = await db.scalars(select(User))
        lists_user_id = [row.id for row in lists_user_id.all()]
        lists_tasks_user_id = await db.scalars(select(Task))
        lists_tasks_user_id = [row.user_id for row in lists_tasks_user_id]
        free_users = []
        for index in lists_user_id:
            if index not in lists_tasks_user_id:
                user = await db.scalar(select(User).where(User.id == index))
                free_users.append(user)
        return free_users

    @classmethod
    async def update_user(cls, db: AsyncSession, user_id: int, data: CreateUser):
        try:
            await db.execute(update(User).where(User.id == user_id).values(
                name=data.name.capitalize(),
                email=data.email.capitalize(),
                hashed_password=bcrypt_context.hash(data.password)
            ))
            await db.commit()

            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'User update is successful'
            }
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Bad request!'
            )
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Bad request!'
            )

    @classmethod
    async def create_user(cls, db: AsyncSession, create_user: CreateUser):
        await db.execute(insert(User).values(
            name=create_user.name.capitalize(),
            email=create_user.email.capitalize(),
            hashed_password=bcrypt_context.hash(create_user.password)
        ))
        await db.commit()

    @classmethod
    async def get_by_id(cls, db: AsyncSession, user_id: int):
        return await db.scalar(select(cls.model).where(cls.model.id == user_id))

    @classmethod
    async def get_by_name(cls, db: AsyncSession, name: str):
        return await db.scalar(select(cls.model).where(cls.model.name == name.capitalize()))

    @classmethod
    async def get_by_email(cls, db: AsyncSession, email: str):
        return await db.scalar(select(cls.model).where(cls.model.email == email.capitalize()))

    @classmethod
    async def delete_user_id(cls, db: AsyncSession, user_id: int):
        value = await db.scalar(select(cls.model).where(cls.model.id == user_id))
        return value

    @classmethod
    async def delete_user_name(cls, db: AsyncSession, name: str):
        value = await db.scalar(select(cls.model).where(cls.model.name == name.capitalize()))
        return value

    @classmethod
    async def delete_user_email(cls, db: AsyncSession, email: str):
        value = await db.scalar(select(cls.model).where(cls.model.email == email.capitalize()))
        return value
