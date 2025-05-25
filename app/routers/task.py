from fastapi import APIRouter, Depends
from typing import Annotated
from app.backend.db_depends import get_db
from app.schemas import CreateTask
from sqlalchemy.ext.asyncio import AsyncSession
from app.routers.auth import get_current_user
from app.is_valid import IsValidData
from app.pattern_repository.TaskRepository import TaskRepository
from app.service.service_task import TaskService

router = APIRouter(prefix='/tasks', tags=['task'])

data = IsValidData()

@router.get('/all')
async def get_all_tasks(db: Annotated[AsyncSession, Depends(get_db)]):
    return await TaskRepository.get_all(db)

@router.get('/')
async def get_task_id(db: Annotated[AsyncSession, Depends(get_db)], task_user_id: int = 0):
    return await TaskService.get_task_user_id(db, task_user_id)

@router.get('/get/title')
async def get_task_title(db: Annotated[AsyncSession, Depends(get_db)], title: str):
    return await TaskService.get_task_title(db, title)

@router.post('/')
async def create_new_task(db: Annotated[AsyncSession, Depends(get_db)], create_task: CreateTask, get_user: Annotated[dict, Depends(get_current_user)]):
    value = await TaskService.create_by_task(db, create_task)
    return value

@router.put('/')
async def update_to_info(db: Annotated[AsyncSession, Depends(get_db)], task_id: int, update_task: CreateTask, get_user: Annotated[dict, Depends(get_current_user)]):
    value = await TaskService.update_task_service(db, update_task, task_id, get_user)
    return value

@router.delete('/')
async def delete_task_id(db: Annotated[AsyncSession, Depends(get_db)], get_user: Annotated[dict, Depends(get_current_user)], task_id: int):
    return await TaskService.del_task_id(db, task_id, get_user)

@router.delete('/del/title')
async def delete_task_title(db: Annotated[AsyncSession, Depends(get_db)], get_user: Annotated[dict, Depends(get_current_user)], title: str):
    return await TaskService.del_task_title(db, title, get_user)