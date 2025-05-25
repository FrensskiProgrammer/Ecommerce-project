from fastapi import APIRouter, Depends
from typing import Annotated
from app.backend.db_depends import get_db
from app.schemas import CreateUser
from sqlalchemy.ext.asyncio import AsyncSession
from app.routers.auth import get_current_user
from app.is_valid import IsValidData
from app.pattern_repository.UserRepository import UserRepository
from app.pattern_repository.TaskRepository import TaskRepository
from app.service.service_user import UserService

router = APIRouter(prefix='/users', tags=['user'])

data = IsValidData()

@router.get('/')
async def get_all_users(db: Annotated[AsyncSession, Depends(get_db)]):
    value = await UserRepository.get_all(db)
    return value

@router.get('/all/free/users')
async def get_free_users(db: Annotated[AsyncSession, Depends(get_db)]):
    value = await UserRepository.get_free_users(db)
    return value

@router.get('/user/id')
async def get_user_id(db: Annotated[AsyncSession, Depends(get_db)], user_id: int):
    return await UserService.get_user_id(db, user_id)

@router.get('/user/name')
async def get_user_name(db: Annotated[AsyncSession, Depends(get_db)], name: str):
    return await UserService.get_user_name(db, name)

@router.get('/user/email')
async def get_user_email(db: Annotated[AsyncSession, Depends(get_db)], email: str):
    return await UserService.get_user_email(db, email)

@router.put('/')
async def update_to_info(db: Annotated[AsyncSession, Depends(get_db)], user_id: int, update_user: CreateUser, get_user: Annotated[dict, Depends(get_current_user)]):
    value = await UserService.update(db, user_id, update_user, get_user)
    return value

@router.delete('/user_id')
async def delete_user_id(db: Annotated[AsyncSession, Depends(get_db)], user_id: int,get_user: Annotated[dict, Depends(get_current_user)]):
    return await UserService.del_by_id(db, user_id, get_user)

@router.delete('/name')
async def delete_user_name(db: Annotated[AsyncSession, Depends(get_db)], name: str, get_user: Annotated[dict, Depends(get_current_user)]):
    return await UserService.del_by_name(db, name, get_user)

@router.delete('/email')
async def delete_user_email(db: Annotated[AsyncSession, Depends(get_db)], email: str, get_user: Annotated[dict, Depends(get_current_user)]):
    return await UserService.del_by_email(db, email, get_user)

@router.get('get_all_tasks_current_user')
async def get_tasks(db: Annotated[AsyncSession, Depends(get_db)], username_id: dict = Depends(get_current_user)):
    return await TaskRepository.get_users_tasks(db, username_id['id'])