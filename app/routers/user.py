from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.is_valid import IsValidData
from app.pattern_repository.TaskRepository import TaskRepository
from app.pattern_repository.UserRepository import UserRepository
from app.routers.auth import get_current_user
from app.schemas import CreateUser
from app.service.service_user import UserService

from app.exceptions.route_protection import base_exception

from sqlalchemy import select
from app.models.user import User

router = APIRouter(prefix="/users", tags=["user"])

data = IsValidData()


@router.get("/")
@base_exception
async def get_all_users(db: Annotated[AsyncSession, Depends(get_db)]):
    """Конечная точка для получения всех пользователей"""

    value = await UserRepository.get_all(db)
    return value


@router.get("/all/free/users")
@base_exception
async def get_free_users(db: Annotated[AsyncSession, Depends(get_db)]):
    """Конечная точка для получения всех пользователей, которые не имеют товары в наличии"""

    value = await UserRepository.get_free_users(db)
    return value


@router.get("/user/id")
@base_exception
async def get_user_id(
    db: Annotated[AsyncSession, Depends(get_db)], user_id: int
):
    """Конечная точка для получения пользователя через его ID"""

    return await UserService.get_user_id(db, user_id)


@router.get("/user/name")
@base_exception
async def get_user_name(
    db: Annotated[AsyncSession, Depends(get_db)], name: str
):
    """Конечная точка для получения пользователя через его имя"""

    return await UserService.get_user_name(db, name)


@router.get("/user/email")
@base_exception
async def get_user_email(
    db: Annotated[AsyncSession, Depends(get_db)], email: str
):
    """Конечная точка для получения пользователя через его почту"""

    return await UserService.get_user_email(db, email)


@router.put("/")
@base_exception
async def update_to_info(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int,
    update_user: CreateUser,
    get_user: Annotated[dict, Depends(get_current_user)],
):
    """Конечная точка для обновления информации о пользователе"""

    value = await UserService.update(db, user_id, update_user, get_user)
    return value


@router.delete("/user_id")
@base_exception
async def delete_user_id(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int,
    get_user: Annotated[dict, Depends(get_current_user)],
):
    """Конечная точка для удаления пользователя через его ID"""

    return await UserService.del_by_id(db, user_id, get_user)


@router.delete("/name")
@base_exception
async def delete_user_name(
    db: Annotated[AsyncSession, Depends(get_db)],
    name: str,
    get_user: Annotated[dict, Depends(get_current_user)],
):
    """Конечная точка для удаления пользователя через его имя"""

    return await UserService.del_by_name(db, name, get_user)


@router.delete("/email")
@base_exception
async def delete_user_email(
    db: Annotated[AsyncSession, Depends(get_db)],
    email: str,
    get_user: Annotated[dict, Depends(get_current_user)],
):
    """Конечная точка для удаления пользователя через его почту"""

    return await UserService.del_by_email(db, email, get_user)


@router.get("/get_all_tasks_current_user")
@base_exception
async def get_tasks(
    db: Annotated[AsyncSession, Depends(get_db)],
    username_id: dict = Depends(get_current_user),
):
    """Конечная точка для получения всех товаров текущего(авторизованного) пользователя"""

    return await TaskRepository.get_users_tasks(db, username_id["id"])

@router.get('/welcome/frensski')
@base_exception
async def welcome_frensski(db: Annotated[AsyncSession, Depends(get_db)]):
    value = await db.scalar(select(User).where(User.names == 'alihan'))
    return value
