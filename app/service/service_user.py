from app.backend.db_depends import AsyncSession
from fastapi import HTTPException, status, Depends
from app.models.user import User
from app.pattern_repository.UserRepository import UserRepository
from fastapi.security import OAuth2PasswordBearer
from app.schemas import CreateUser
from app.is_valid import IsValidData
from sqlalchemy import select
from typing import Annotated
from sqlalchemy import insert
from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import IntegrityError
import jwt


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

class UserService(UserRepository):

    @classmethod
    async def get_user_id(cls, db: AsyncSession, user_id):
        value = await UserRepository.get_by_id(db, user_id)

        if not value:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found!'
            )
        return value

    @classmethod
    async def get_user_name(cls, db: AsyncSession, name):
        value = await UserRepository.get_by_name(db, name)

        if not value:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found!'
            )
        return value

    @classmethod
    async def get_user_email(cls, db: AsyncSession, email):
        value = await UserRepository.get_by_email(db, email)

        if not value:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found!'
            )
        return value

    @classmethod
    async def update(cls, db: AsyncSession, user_id, update_user: CreateUser, get_user: Annotated[dict, Depends(get_current_user)]):
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
            await UserRepository.update_user(db, user_id, update_user)
            return {
                'status': status.HTTP_200_OK,
                'message': 'User succesfull updated!'
            }

    @classmethod
    async def del_by_id(cls, db: AsyncSession, user_id: int, get_user: Annotated[dict, Depends(get_current_user)]):
        value = await UserRepository.delete_user_id(db, user_id)

        if value is None:
            return {
                'status_code': status.HTTP_404_NOT_FOUND,
                'transaction': 'User not found'
            }

        if get_user.get('id') == value.id:
            value = await UserRepository.delete_user_id(db, user_id)
            await db.delete(value)
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'User delete is successful'
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='This User does not belong to you'
            )

    @classmethod
    async def del_by_name(cls, db: AsyncSession, name: str, get_user: Annotated[dict, Depends(get_current_user)]):
        value = await UserRepository.delete_user_name(db, name)

        if value is None:
            return {
                'status_code': status.HTTP_404_NOT_FOUND,
                'transaction': 'User not found'
            }

        if get_user.get('id') == value.id:
            value = await UserRepository.delete_user_name(db, name)
            await db.delete(value)
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'User delete is successful'
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='This User does not belong to you'
            )

    @classmethod
    async def del_by_email(cls, db: AsyncSession, email: str, get_user: Annotated[dict, Depends(get_current_user)]):
        value = await UserRepository.delete_user_email(db, email)

        if value is None:
            return {
                'status_code': status.HTTP_404_NOT_FOUND,
                'transaction': 'User not found'
            }

        if get_user.get('id') == value.id:
            value = await UserRepository.delete_user_email(db, email)
            await db.delete(value)
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'User delete is successful'
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='This User does not belong to you'
            )

    @classmethod
    async def create_new_user(cls, db: AsyncSession, create_user: CreateUser):
        try:
            lists = await db.scalars(select(User))
            lists = [[row.name.capitalize(), row.email.capitalize()] for row in lists.all()]
            lists_name_email = [[row[0] for row in lists], [row[1] for row in lists]]
            if not (data.is_valid_username(create_user.name)) or create_user.name.capitalize() in lists_name_email[0]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Invalid name or already in use'
                )
            elif not (data.is_valid_email(create_user.email)) or create_user.email.capitalize() in lists_name_email[1]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Invalid email or already in use'
                )
            elif not (data.is_valid_password(create_user.password)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Invalid password'
                )
            else:
                await UserRepository.create_user(db, create_user)
                return {
                    'status_code': status.HTTP_201_CREATED,
                    'transaction': 'Successful'
                }

        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email or name already exists."
            )
