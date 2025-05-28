from datetime import datetime, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.backend.db_depends import AsyncSession
from app.is_valid import IsValidData
from app.models.task import Task
from app.models.user import User
from app.pattern_repository.TaskRepository import TaskRepository
from app.schemas import CreateTask
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



class TaskService(TaskRepository):
    """Класс, в котором содержится вся проверка конечных точек"""

    @classmethod
    async def get_task_user_id(cls, db: AsyncSession, user_id: int):
        """Получает задачу по ID пользователя из репозитория.

        Args:
            db (AsyncSession): Асинхронная сессия базы данных
            user_id (int): ID пользователя для поиска задачи

        Returns:
            Task: Объект найденной задачи

        Raises:
            HTTPException: 404 NOT_FOUND - если задача не найдена
            HTTPException: 500 INTERNAL_SERVER_ERROR - при ошибках БД

        Notes:
            - Использует TaskRepository для доступа к данным
            - Возвращает полный объект задачи
        """

        value = await TaskRepository.get_by_user_id(db, user_id)

        if value is None:
            raise TaskNotFound()
        return value

    @classmethod
    async def get_task_title(cls, db: AsyncSession, title: str):
        """Получает задачу по точному совпадению названия.

        Args:
            db (AsyncSession): Асинхронная сессия подключения к БД
            title (str): Название задачи для поиска (точное совпадение)

        Returns:
            Task: Объект найденной задачи со всеми полями

        Raises:
            HTTPException: 404 NOT_FOUND - если задача с указанным названием не существует
            HTTPException: 500 INTERNAL_SERVER_ERROR - при ошибках работы с БД

        Notes:
            - Поиск выполняется по точному совпадению названия (case-sensitive)
            - Использует TaskRepository.get_by_title для получения данных
            - Возвращает полный объект задачи со всеми отношениями
        """

        value = await TaskRepository.get_by_title(db, title)

        if value is None:
            raise TaskNotFound()
        return value

    @classmethod
    async def create_by_task(cls, db: AsyncSession, create_task: CreateTask):
        """Создает новую задачу с валидацией входных данных.

        Выполняет комплексную проверку перед созданием задачи:
        - Уникальность названия задачи (case-insensitive)
        - Валидность статуса
        - Валидность описания
        - Существование связанного пользователя

        Args:
            db (AsyncSession): Асинхронная сессия подключения к БД
            create_task (CreateTask): DTO с данными для создания задачи

        Returns:
            dict: Результат операции:
                - status (int): HTTP статус код
                - message (str): Сообщение о результате

        Raises:
            HTTPException: 403 FORBIDDEN - при:
                - дублировании названия задачи
                - невалидном статусе
                - невалидном описании
            HTTPException: 404 NOT_FOUND - при ошибках целостности данных
            HTTPException: 500 INTERNAL_SERVER_ERROR - при других ошибках БД

        Notes:
            - Название задачи нормализуется (capitalize) перед проверкой уникальности
            - Использует TaskRepository.create_task для сохранения
            - Валидация выполняется через методы data.is_valid_*
        """

        try:
            lists_id = await db.scalars(select(User))
            lists_id = [obj.id for obj in lists_id.all()]
            lists_title = await db.scalars(select(Task))
            lists_title = [row.title.capitalize() for row in lists_title.all()]
            lists_user_id = await db.scalars(select(Task))
            lists_user_id = [row.user_id for row in lists_user_id.all()]

            if (not (data.is_valid_title(create_task.title))) or (
                create_task.title.capitalize() in lists_title
            ):
                raise InvalidTitleTask()
            elif not (data.is_valid_status(create_task.status)):
                raise InvalidStatusTask()
            elif not (data.is_valid_description(create_task.description)):
                raise InvalidDescTask()
            else:
                await TaskRepository.create_task(db, create_task)

                return {
                    "status": status.HTTP_201_CREATED,
                    "message": "Task successful created!",
                }

        except IntegrityError:
            raise IntegError()

    @classmethod
    async def update_task_service(
        cls,
        db: AsyncSession,
        update_task: CreateTask,
        task_id,
        get_user: Annotated[dict, Depends(get_current_user)],
    ):
        """Обновляет существующую задачу с комплексной валидацией.

        Выполняет проверки перед обновлением:
        - Права доступа пользователя к задаче
        - Уникальность нового названия задачи
        - Валидность статуса и описания
        - Существование задачи

        Args:
            db (AsyncSession): Асинхронная сессия БД
            update_task (CreateTask): DTO с обновляемыми данными задачи
            task_id (int): ID обновляемой задачи
            get_user (dict): Текущий аутентифицированный пользователь (из Depends)

        Returns:
            dict: Результат операции:
                - status (int): HTTP 200 при успехе
                - message (str): Сообщение о результате

        Raises:
            HTTPException: 403 FORBIDDEN - при:
                - нарушении уникальности названия
                - невалидных данных
            HTTPException: 404 NOT_FOUND - при:
                - отсутствии прав доступа
                - несуществующей задаче
                - ошибках целостности
            HTTPException: 500 INTERNAL_SERVER_ERROR - при ошибках БД

        Notes:
            - Проверяет принадлежность задачи пользователю
            - Название нормализуется (capitalize) при проверке уникальности
            - Использует TaskRepository.update_by для сохранения изменений
            - Валидация через data.is_valid_* методы
        """

        try:
            lists_id = await db.scalars(select(User))
            lists_id = [obj.id for obj in lists_id.all()]
            lists_title = await db.scalars(select(Task))
            lists_title = [row.title for row in lists_title.all()]
            lists_user_id = await db.scalars(select(Task))
            lists_user_id = [row.user_id for row in lists_user_id.all()]

            create_task = update_task

            if get_user.get("id") != task_id:
                raise NoUseTask()
            elif (not (data.is_valid_title(create_task.title))) or (
                create_task.title.capitalize() in lists_title
            ):
                raise InvalidTitleTask()
            elif not (data.is_valid_status(create_task.status)):
                raise InvalidStatusTask()
            elif not (data.is_valid_description(create_task.description)):
                raise InvalidDescTask()
            if task_id not in lists_user_id:
                raise TaskNotFound()
            else:

                await TaskRepository.update_by(db, update_task, task_id)
                return {
                    "status": status.HTTP_200_OK,
                    "message": "Successful update tasks",
                }

        except IntegrityError:
            raise TaskNotFound()

    @classmethod
    async def del_task_id(
        cls,
        db: AsyncSession,
        task_id: int,
        get_user: Annotated[dict, Depends(get_current_user)],
    ):
        """Удаляет задачу по ID после проверки прав доступа.

        Выполняет двухэтапную проверку:
        1. Существование задачи с указанным ID
        2. Принадлежность задачи текущему пользователю

        Args:
            db (AsyncSession): Асинхронная сессия подключения к БД
            task_id (int): ID задачи для удаления
            get_user (dict): Данные текущего пользователя (из зависимости get_current_user)

        Returns:
            dict: Результат операции:
                - status (int): HTTP 200 при успешном удалении
                - message (str): Подтверждающее сообщение

        Raises:
            HTTPException: 404 NOT_FOUND - если задача не существует
            HTTPException: 403 FORBIDDEN - если задача принадлежит другому пользователю
            HTTPException: 500 INTERNAL_SERVER_ERROR - при ошибках БД

        Notes:
            - Использует TaskRepository.del_by_id для поиска задачи
            - Проверяет соответствие user_id задачи и текущего пользователя
            - Выполняет физическое удаление записи из БД
        """

        value = await TaskRepository.del_by_id(db, task_id)

        if value is None:
            raise TaskNotFound()

        if get_user.get("id") == value.user_id:
            value = await TaskRepository.del_by_id(db, task_id)
            await db.delete(value)
            await db.commit()
            return {
                "status": status.HTTP_200_OK,
                "message": "Task succesful deleted",
            }
        else:
            raise NoUseTask()

    @classmethod
    async def del_task_title(
        cls,
        db: AsyncSession,
        title: str,
        get_user: Annotated[dict, Depends(get_current_user)],
    ):
        """Удаляет задачу по названию после проверки прав доступа.

        Args:
            db (AsyncSession): Асинхронная сессия БД
            title (str): Название задачи для удаления (точное совпадение)
            get_user (dict): Данные аутентифицированного пользователя из токена

        Returns:
            dict: Результат операции:
                - status (int): HTTP_200_OK при успехе
                - message (str): 'Task successful deleted'

        Raises:
            HTTPException: 404_NOT_FOUND - если задача не найдена
            HTTPException: 403_FORBIDDEN - если задача принадлежит другому пользователю

        Notes:
            - Поиск задачи выполняется по точному совпадению названия
            - Проверяет соответствие user_id задачи и текущего пользователя
            - Использует TaskRepository.del_by_title для поиска задачи
            - Выполняет физическое удаление через сессию БД
        """

        value = await TaskRepository.del_by_title(db, title)

        if value is None:
            raise TaskNotFound()

        if get_user.get("id") == value.user_id:
            value = await TaskRepository.del_by_title(db, title)
            await db.delete(value)
            await db.commit()
            return {
                "status": status.HTTP_200_OK,
                "message": "Task succesful deleted",
            }
        else:
            raise NoUseTask()
