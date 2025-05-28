from datetime import datetime, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.backend.db_depends import AsyncSession
from app.is_valid import IsValidData
from app.models.user import User
from app.pattern_repository.UserRepository import UserRepository
from app.schemas import CreateUser
from app.settings.config import Settings

from app.exceptions.exceptions import *

data = IsValidData()

SECRET_KEY = Settings.secret_key
ALGORITHM = Settings.algorithm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """Аутентифицирует пользователя по JWT-токену и возвращает его данные.

    Args:
        token (str): JWT-токен из заголовка Authorization (OAuth2 Bearer token).

    Returns:
        dict: Словарь с данными пользователя:
            - username (str): Логин пользователя (subject из токена)
            - id (int): ID пользователя

    Raises:
        HTTPException: 401 UNAUTHORIZED - если:
            - токен просрочен (ExpiredSignatureError)
            - невалидный username/subject
            - общая ошибка валидации токена
        HTTPException: 400 BAD_REQUEST - если:
            - отсутствует expire в токене
            - некорректный формат токена
    """

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        user_id: int | None = payload.get("id")
        expire: int | None = payload.get("exp")

        if username is None:
            raise UserNotAutorized()

        if expire is None:
            raise NoAccesToken()

        if not isinstance(expire, int):
            raise TokenExpired()

        # Проверка срока действия токена
        current_time = datetime.now(timezone.utc).timestamp()

        if expire < current_time:
            raise TokenExpired()

        return {"username": username, "id": user_id}

    except jwt.ExpiredSignatureError:
        raise TokenExpired()
    except jwt.exceptions:
        raise UserNotAutorized()


class UserService(UserRepository):

    @classmethod
    async def get_user_id(cls, db: AsyncSession, user_id):
        """Получает пользователя по его ID из репозитория.

        Args:
            db (AsyncSession): Асинхронная сессия для работы с БД
            user_id (int): Идентификатор пользователя для поиска

        Returns:
            User: Объект пользователя со всеми полями

        Raises:
            HTTPException: 404 NOT_FOUND - если пользователь с указанным ID не найден
            HTTPException: 500 INTERNAL_SERVER_ERROR - при ошибках работы с БД

        Notes:
            - Использует UserRepository.get_by_id для получения данных
            - Возвращает полный объект пользователя со всеми атрибутами
        """

        value = await UserRepository.get_by_id(db, user_id)

        if not value:
            raise NotFoundUser()
        return value

    @classmethod
    async def get_user_name(cls, db: AsyncSession, name):
        """Асинхронная класс-метод-функция для получения имени пользователя по указанному имени.
        :param cls: Класс метода. :param db:
        Экземпляр асинхронной сессии базы данных (`AsyncSession`).
        :param name: Имя пользователя для поиска. :
        return: Запрошенный объект пользователя из БД.
        :raises HTTPException: Если пользователь с указанным именем не найден.
        """

        value = await UserRepository.get_by_name(db, name)

        if not value:
            raise NotFoundUser()
        return value

    @classmethod
    async def get_user_email(cls, db: AsyncSession, email):
        """Метод для получения пользователя через его почту"""

        value = await UserRepository.get_by_email(db, email)

        if not value:
            raise NotFoundUser()
        return value

    @classmethod
    async def update(
        cls,
        db: AsyncSession,
        user_id,
        update_user: CreateUser,
        get_user: Annotated[dict, Depends(get_current_user)],
    ):
        """Метод для обновления информации о пользователе с проверкой на валидности данных"""

        lists_id = await db.scalars(select(User))
        lists_id = [[row.id, row.name, row.email] for row in lists_id.all()]
        lists_all = [
            [x[0] for x in lists_id],
            [x[1] for x in lists_id],
            [x[2] for x in lists_id],
        ]

        if user_id != get_user.get("id"):
            raise DeleteUser()

        elif user_id not in lists_all[0]:
            raise NotFoundUser()

        elif not (data.is_valid_username(update_user.name)) or (
            update_user.name.capitalize() in lists_all[1]
        ):
            raise InvalidName()

        elif not (data.is_valid_email(update_user.email)) or (
            update_user.email.capitalize() in lists_all[2]
        ):
            raise InvalidEmail()

        elif not (data.is_valid_password(update_user.password)):
            raise InvalidPasswd()

        else:
            await UserRepository.update_user(db, user_id, update_user)
            return {
                "status": status.HTTP_200_OK,
                "message": "User succesfull updated!",
            }

    @classmethod
    async def del_by_id(
        cls,
        db: AsyncSession,
        user_id: int,
        get_user: Annotated[dict, Depends(get_current_user)],
    ):
        """Метод для удаления пользователя через его ID"""

        value = await UserRepository.delete_user_id(db, user_id)

        if value is None:
            return {
                "status_code": status.HTTP_404_NOT_FOUND,
                "transaction": "User not found",
            }

        if get_user.get("id") == value.id:
            value = await UserRepository.delete_user_id(db, user_id)
            await db.delete(value)
            await db.commit()
            return {
                "status_code": status.HTTP_200_OK,
                "transaction": "User delete is successful",
            }
        else:
            raise DeleteUser()

    @classmethod
    async def del_by_name(
        cls,
        db: AsyncSession,
        name: str,
        get_user: Annotated[dict, Depends(get_current_user)],
    ):
        """Метод для удаления пользователя через его имя"""

        value = await UserRepository.delete_user_name(db, name)

        if value is None:
            return {
                "status_code": status.HTTP_404_NOT_FOUND,
                "transaction": "User not found",
            }

        if get_user.get("id") == value.id:
            value = await UserRepository.delete_user_name(db, name)
            await db.delete(value)
            await db.commit()
            return {
                "status_code": status.HTTP_200_OK,
                "transaction": "User delete is successful",
            }
        else:
            raise DeleteUser()

    @classmethod
    async def del_by_email(
        cls,
        db: AsyncSession,
        email: str,
        get_user: Annotated[dict, Depends(get_current_user)],
    ):
        """Метод для удаления пользователя через его почту"""

        value = await UserRepository.delete_user_email(db, email)

        if value is None:
            return {
                "status_code": status.HTTP_404_NOT_FOUND,
                "transaction": "User not found",
            }

        if get_user.get("id") == value.id:
            value = await UserRepository.delete_user_email(db, email)
            await db.delete(value)
            await db.commit()
            return {
                "status_code": status.HTTP_200_OK,
                "transaction": "User delete is successful",
            }
        else:
            raise DeleteUser()

    @classmethod
    async def create_new_user(cls, db: AsyncSession, create_user: CreateUser):
        """Метод для создания пользователя со всеми проверками данных"""

        try:
            lists = await db.scalars(select(User))
            lists = [
                [row.name.capitalize(), row.email.capitalize()]
                for row in lists.all()
            ]
            lists_name_email = [
                [row[0] for row in lists],
                [row[1] for row in lists],
            ]
            if (
                not (data.is_valid_username(create_user.name))
                or create_user.name.capitalize() in lists_name_email[0]
            ):
                raise InvalidName()
            elif (
                not (data.is_valid_email(create_user.email))
                or create_user.email.capitalize() in lists_name_email[1]
            ):
                raise InvalidEmail()
            elif not (data.is_valid_password(create_user.password)):
                raise InvalidPasswd()
            else:
                await UserRepository.create_user(db, create_user)
                return {
                    "status_code": status.HTTP_201_CREATED,
                    "transaction": "Successful",
                }

        except IntegrityError:
            raise InvalidEmail()
