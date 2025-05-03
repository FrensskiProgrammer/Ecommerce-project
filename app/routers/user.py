from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from sqlalchemy import insert, select, update
from slugify import slugify
from app.backend.db_depends import get_db
from app.schemas import CreateUser
from app.models.user import User
from app.models.task import Task
from sqlalchemy.ext.asyncio import AsyncSession
from app.routers.auth import get_current_user
from sqlalchemy.exc import IntegrityError
from app.is_valid import IsValidData

router = APIRouter(prefix='/users', tags=['user'])

data = IsValidData()

@router.get('/')
async def get_all_users(db: Annotated[AsyncSession, Depends(get_db)]):
    users_list = await db.scalars(select(User))
    return users_list.all()

@router.get('/{user_id}')
async def get_user(db: Annotated[AsyncSession, Depends(get_db)], user_id: int):
    lists_id = await db.scalars(select(User))
    lists_id = [row.id for row in lists_id.all()]
    if user_id in lists_id:
        user = await db.scalar(select(User).where(User.id == user_id))
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found!'
        )

@router.put('/')
async def update_to_info(db: Annotated[AsyncSession, Depends(get_db)], user_id: int, update_user: CreateUser, get_user: Annotated[dict, Depends(get_current_user)]):
    lists_id = await db.scalars(select(User))
    lists_id = [[row.id, row.name, row.email] for row in lists_id.all()]
    lists_all = [[x[0] for x in lists_id], [x[1] for x in lists_id], [x[2] for x in lists_id]]

    if user_id != get_user.get('id'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete someone else's user"
        )

    elif user_id not in lists_all[0]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )

    elif not (data.is_valid_username(update_user.name)) or (update_user.name.capitalize() in lists_all[1]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Invalid name or already in use'
        )

    elif not (data.is_valid_email(update_user.email)) or (update_user.email.capitalize() in lists_all[2]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Invalid email or already in use'
        )

    elif not (data.is_valid_password(update_user.password)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Invalid password'
        )

    else:
        user = await db.scalar(select(User).where(User.id == user_id))
        user.name = update_user.name.capitalize()
        user.email = update_user.email.capitalize()
        user.password = update_user.password

        await db.commit()

        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'User update is successful'
        }

@router.delete('/')
async def delete_user(db: Annotated[AsyncSession, Depends(get_db)], user_id: int, get_user: Annotated[dict, Depends(get_current_user)]):
    lists_id = await db.scalars(select(User))
    lists_id = [row.id for row in lists_id.all()]
    if user_id in lists_id:
        del_user = await db.scalar(select(User).where(User.id == user_id))
        if get_user.get('id') == del_user.id:
            user = await db.scalar(select(User).where(User.id == user_id))
            await db.delete(user)
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'User delete is successful'
            }
        else:
            return {
                'status': status.HTTP_403_FORBIDDEN,
                'detail': 'this product does not belong to you'
            }
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found!'
        )