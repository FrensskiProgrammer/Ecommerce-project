from app.pattern_repository.TaskRepository import TaskRepository
from app.models.task import Task
from app.backend.db_depends import AsyncSession
from fastapi import HTTPException, status
from app.schemas import CreateTask
from sqlalchemy import select
from app.models.user import User
from sqlalchemy.exc import IntegrityError
from typing import Annotated
from fastapi import Depends
from app.is_valid import IsValidData
import jwt
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timezone


data = IsValidData()

SECRET_KEY = 'c86972cf29846cd228d02f3564e9d2802c101a807003dda96a970a8e5b7b562f'
ALGORITHM = 'HS256'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get('sub')
        user_id: int | None = payload.get('id')
        expire: int | None = payload.get('exp')

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate user'
            )
        if expire is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token supplied"
            )

        if not isinstance(expire, int):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token format"
            )

        # Проверка срока действия токена
        current_time = datetime.now(timezone.utc).timestamp()

        if expire < current_time:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired!"
            )

        return {
            'username': username,
            'id': user_id
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired!"
        )
    except jwt.exceptions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user'
        )


class TaskService(TaskRepository):

    @classmethod
    async def get_task_user_id(cls, db: AsyncSession, user_id: int):
        value = await TaskRepository.get_by_user_id(db, user_id)

        if value is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Task not found!'
            )
        return value

    @classmethod
    async def get_task_title(cls, db: AsyncSession, title: str):
        value = await TaskRepository.get_by_title(db, title)

        if value is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Task not found!'
            )
        return value

    @classmethod
    async def create_by_task(cls, db: AsyncSession, create_task: CreateTask):
        try:
            lists_id = await db.scalars(select(User))
            lists_id = [obj.id for obj in lists_id.all()]
            lists_title = await db.scalars(select(Task))
            lists_title = [row.title.capitalize() for row in lists_title.all()]
            lists_user_id = await db.scalars(select(Task))
            lists_user_id = [row.user_id for row in lists_user_id.all()]

            if (not (data.is_valid_description(create_task.title))) or (create_task.title.capitalize() in lists_title):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='This name already exists or the id was not found or invalid'
                )
            elif not (data.is_valid_status(create_task.status)):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='Invalid status'
                )
            elif not (data.is_valid_description(create_task.description)):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='Invalid description'
                )
            else:
                await TaskRepository.create_task(db, create_task)

                return {
                    'status': status.HTTP_201_CREATED,
                    'message': 'Task successful created!'
                }

        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Error'
            )

    @classmethod
    async def update_task_service(cls, db: AsyncSession, update_task: CreateTask, task_id, get_user: Annotated[dict, Depends(get_current_user)]):
        try:
            lists_id = await db.scalars(select(User))
            lists_id = [obj.id for obj in lists_id.all()]
            lists_title = await db.scalars(select(Task))
            lists_title = [row.title for row in lists_title.all()]
            lists_user_id = await db.scalars(select(Task))
            lists_user_id = [row.user_id for row in lists_user_id.all()]

            create_task = update_task

            if get_user.get('id') != task_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='This item does not belong to you and you do not have access to it'
                )

            elif (not (data.is_valid_description(create_task.title))) or (
                    create_task.title.capitalize() in lists_title):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='This name already exists or the id was not found or invalid'
                )
            elif not (data.is_valid_status(create_task.status)):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='Invalid status'
                )
            elif not (data.is_valid_description(create_task.description)):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='Invalid description'
                )
            if task_id not in lists_user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='ID does not exist or is busy!'
                )
            else:

                await TaskRepository.update_by(db, update_task, task_id)
                return {
                    'status': status.HTTP_200_OK,
                    'message': 'Successful update tasks'
                }



        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='ID does not exist or is busy!'
            )

    @classmethod
    async def del_task_id(cls, db: AsyncSession, task_id: int, get_user: Annotated[dict, Depends(get_current_user)]):
        value = await TaskRepository.del_by_id(db, task_id)

        if value is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Task not found!'
            )

        if get_user.get('id') == value.user_id:
            value = await TaskRepository.del_by_id(db, task_id)
            await db.delete(value)
            await db.commit()
            return {
                'status': status.HTTP_200_OK,
                'message': 'Task succesful deleted'
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='This Task does not belong to you'
            )

    @classmethod
    async def del_task_title(cls, db: AsyncSession, title: str, get_user: Annotated[dict, Depends(get_current_user)]):
        value = await TaskRepository.del_by_title(db, title)

        if value is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Task not found!'
            )

        if get_user.get('id') == value.user_id:
            value = await TaskRepository.del_by_title(db, title)
            await db.delete(value)
            await db.commit()
            return {
                'status': status.HTTP_200_OK,
                'message': 'Task succesful deleted'
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='This Task does not belong to you'
            )



