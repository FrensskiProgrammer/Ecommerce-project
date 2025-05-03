from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from sqlalchemy import insert, select, update
from slugify import slugify
from app.backend.db_depends import get_db
from app.schemas import CreateTask
from app.models.user import User
from app.models.task import Task
from sqlalchemy.ext.asyncio import AsyncSession
from app.routers.auth import get_current_user
from sqlalchemy.exc import IntegrityError
from app.is_valid import IsValidData

router = APIRouter(prefix='/tasks', tags=['task'])

data = IsValidData()

@router.get('/')
async def get_all_tasks(db: Annotated[AsyncSession, Depends(get_db)]):
    tasks_list = await db.scalars(select(Task))
    return tasks_list.all()

@router.get('/{task_id}')
async def get_task(db: Annotated[AsyncSession, Depends(get_db)], task_id: int):
    lists_id = await db.scalars(select(Task))
    lists_id = [row.id for row in lists_id.all()]
    if task_id not in lists_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Tasks not found!'
        )
    else:
        task = await db.scalar(select(Task).where(Task.id == task_id))
        return task

@router.post('/')
async def create_new_task(db: Annotated[AsyncSession, Depends(get_db)], create_task: CreateTask, get_user: Annotated[dict, Depends(get_current_user)]):
    try:
        lists_id = await db.scalars(select(User))
        lists_id = [obj.id for obj in lists_id.all()]
        lists_title = await db.scalars(select(Task))
        lists_title = [row.title for row in lists_title.all()]
        lists_user_id = await db.scalars(select(Task))
        lists_user_id = [row.user_id for row in lists_user_id.all()]

        if (not(data.is_valid_description(create_task.title))) or (create_task.title.capitalize() in lists_title):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='This name already exists or the id was not found or invalid'
            )
        elif not(data.is_valid_status(create_task.status)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Invalid status'
            )
        elif not(data.is_valid_description(create_task.description)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Invalid description'
            )
        elif (create_task.user_id in lists_user_id) or (create_task.user_id not in lists_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='This ID is already taken by another user or does not exist'
            )
        else:
            await db.execute(insert(Task).values(title=create_task.title.capitalize(),
                                                 description=create_task.description,
                                                 status=create_task.status,
                                                 user_id=create_task.user_id))
            await db.commit()

            return {
                'status': status.HTTP_201_CREATED,
                'message': 'Successful created task'
            }

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Error'
        )

@router.put('/')
async def update_to_info(db: Annotated[AsyncSession, Depends(get_db)], task_id: int, update_task: CreateTask, get_user: Annotated[dict, Depends(get_current_user)]):
    try:
        lists_id = await db.scalars(select(User))
        lists_id = [obj.id for obj in lists_id.all()]
        lists_title = await db.scalars(select(Task))
        lists_title = [row.title for row in lists_title.all()]
        lists_user_id = await db.scalars(select(Task))
        lists_user_id = [row.user_id for row in lists_user_id.all()]
        # lists_id_task = await db.scalars(select(Task))
        # lists_id_task = [row.user_id for row in lists_id_task.all()]

        create_task = update_task

        if get_user.get('id') != task_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='This item does not belong to you and you do not have access to it'
            )

        elif (not(data.is_valid_description(create_task.title))) or (create_task.title.capitalize() in lists_title):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='This name already exists or the id was not found or invalid'
            )
        elif not(data.is_valid_status(create_task.status)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Invalid status'
            )
        elif not(data.is_valid_description(create_task.description)):
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
            await db.execute(update(Task).where(Task.user_id == task_id).values(
                                                title=create_task.title.capitalize(),
                                                description=create_task.description,
                                                status=create_task.status,
                                                user_id=create_task.user_id))
            await db.commit()

            return {
                'status': status.HTTP_200_OK,
                'message': 'Successful update tasks'
            }



    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='ID does not exist or is busy!'
        )

@router.delete('/')
async def delete_task(db: Annotated[AsyncSession, Depends(get_db)], task_id: int, get_user: Annotated[dict, Depends(get_current_user)]):
    lists_user_id = await db.scalars(select(Task))
    lists_user_id = [row.user_id for row in lists_user_id.all()]
    if task_id not in lists_user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='ID not found!'
        )
    else:
        if get_user.get('id') == task_id:
            task = await db.scalar(select(Task).where(Task.user_id == task_id))
            await db.delete(task)
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'Task delete is successful'
            }
        else:
            return {
                'status': status.HTTP_403_FORBIDDEN,
                'detail': 'This product does not belong to you'
            }