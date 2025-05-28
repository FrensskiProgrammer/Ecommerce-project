from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.is_valid import IsValidData
from app.models.user import User
from app.schemas import CreateUser
from app.service.service_user import UserService
from app.settings.config import Settings

from app.exceptions.route_protection import base_exception

data = IsValidData()

SECRET_KEY = Settings.secret_key
ALGORITHM = Settings.algorithm

router = APIRouter(prefix="/auth", tags=["auth"])
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


@router.post("/")
@base_exception
async def create_user(
    db: Annotated[AsyncSession, Depends(get_db)], create_user: CreateUser
):
    """Конечная точка для создания пользователя"""

    value = await UserService.create_new_user(db, create_user)
    return value


async def authenticate_user(
    db: Annotated[AsyncSession, Depends(get_db)], username: str, password: str
):
    """Аутентифицирует пользователя по логину и паролю.

    Проверяет существование пользователя и соответствие хеша пароля.

    Args:
        db (AsyncSession): Асинхронная сессия SQLAlchemy
        username (str): Логин пользователя для аутентификации
        password (str): Пароль в чистом виде для проверки

    Returns:
        User: Объект аутентифицированного пользователя

    Raises:
        HTTPException: 401 UNAUTHORIZED - если:
            - пользователь не найден
            - неверный пароль
        HTTPException: 500 INTERNAL_SERVER_ERROR - при ошибках БД

    Notes:
        - Использует bcrypt для проверки хеша пароля
        - Добавляет WWW-Authenticate header при ошибках
        - Требует предварительно хешированный пароль в БД
    """
    user = await db.scalar(select(User).where(User.name == username))
    if not user or not bcrypt_context.verify(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post("/token")
@base_exception
async def login(
    db: Annotated[AsyncSession, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    """Конечная точка для получения текущего токена пользователя"""

    user = await authenticate_user(db, form_data.username, form_data.password)

    token = await create_access_token(
        user.name, user.id, expires_delta=timedelta(minutes=20)
    )
    return {"access_token": token, "token_type": "bearer"}


async def create_access_token(
    username: str, user_id: int, expires_delta: timedelta
):
    """Генерирует JWT-токен доступа с указанными данными пользователя.

    Args:
        username (str): Логин пользователя (будет сохранён в поле 'sub' токена)
        user_id (int): ID пользователя (будет сохранён в поле 'id' токена)
        expires_delta (timedelta): Время жизни токена (от текущего момента)

    Returns:
        str: Сгенерированный JWT-токен в виде строки

    Notes:
        - Временная метка expiration (exp) автоматически преобразуется в UNIX timestamp
        - Для подписи используется SECRET_KEY и ALGORITHM, определённые в модуле
    """
    payload = {
        "sub": username,
        "id": user_id,
        "exp": datetime.now(timezone.utc) + expires_delta,
    }

    # Преобразование datetime в timestamp (количество секунд с начала эпохи)
    payload["exp"] = int(payload["exp"].timestamp())
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


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
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user",
            )
        if expire is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token supplied",
            )

        if not isinstance(expire, int):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token format",
            )

        # Проверка срока действия токена
        current_time = datetime.now(timezone.utc).timestamp()

        if expire < current_time:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired!",
            )

        return {"username": username, "id": user_id}
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired!"
        )
    except jwt.exceptions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user",
        )


@router.get("/read_current_user")
@base_exception
async def read_current_user(user: dict = Depends(get_current_user)):
    """Конечная точка для получения объекта пользователя(ID и username)"""

    return {"Users": user}
