from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.is_valid import IsValidData
from app.pattern_repository.TaskRepository import TaskRepository
from app.routers.auth import get_current_user
from app.schemas import CreateTask
from app.service.service_task import TaskService

from app.exceptions.route_protection import base_exception

router = APIRouter(prefix="/tasks", tags=["task"])

data = IsValidData()


@router.get("/all")
@base_exception
async def get_all_tasks(db: Annotated[AsyncSession, Depends(get_db)]):
    """Конечная точка для получения всех задач"""

    return await TaskRepository.get_all(db)


@router.get("/")
@base_exception
async def get_task_id(
    db: Annotated[AsyncSession, Depends(get_db)], task_user_id: int = 0
):
    """Конечная точка для получения задачи через ее ID"""

    return await TaskService.get_task_user_id(db, task_user_id)


@router.get("/get/title")
@base_exception
async def get_task_title(
    db: Annotated[AsyncSession, Depends(get_db)], title: str
):
    """Конечная точка для получения задачи через ее название"""

    return await TaskService.get_task_title(db, title)


@router.post("/")
@base_exception
async def create_new_task(
    db: Annotated[AsyncSession, Depends(get_db)],
    create_task: CreateTask,
    get_user: Annotated[dict, Depends(get_current_user)],
):
    """Конечная точка для создания новой задачи"""

    value = await TaskService.create_by_task(db, create_task)
    return value


@router.put("/")
@base_exception
async def update_to_info(
    db: Annotated[AsyncSession, Depends(get_db)],
    task_id: int,
    update_task: CreateTask,
    get_user: Annotated[dict, Depends(get_current_user)],
):
    """Конечная точка для обновления информации о задаче"""

    value = await TaskService.update_task_service(
        db, update_task, task_id, get_user
    )
    return value


@router.delete("/")
@base_exception
async def delete_task_id(
    db: Annotated[AsyncSession, Depends(get_db)],
    get_user: Annotated[dict, Depends(get_current_user)],
    task_id: int,
):
    """Конечная точка для удаления задачи через ее ID"""

    return await TaskService.del_task_id(db, task_id, get_user)


@router.delete("/del/title")
@base_exception
async def delete_task_title(
    db: Annotated[AsyncSession, Depends(get_db)],
    get_user: Annotated[dict, Depends(get_current_user)],
    title: str,
):
    """Конечная точка для удаления задачи через ее название"""

    return await TaskService.del_task_title(db, title, get_user)


@router.get("get/free/tasks")
@base_exception
async def get_free_tasks(db: Annotated[AsyncSession, Depends(get_db)]):
    """Конечная точка для получения всех задач, которые не имеют владельца"""

    return await TaskRepository.get_free_tasks(db)
