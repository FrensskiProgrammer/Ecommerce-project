from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
from app.exceptions.exceptions import *
from re import search

lists_classes = [NotFoundUser, DeleteUser, InvalidName, InvalidEmail, InvalidPasswd,
                 UserNotAutorized, NoAccesToken, InvalidToken, TokenExpired,
                 TaskNotFound, InvalidStatusTask, InvalidTitleTask, InvalidDescTask,
                 IntegError, NoUseTask]

def base_exception(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return result
        except SQLAlchemyError as error:
            return f'Непредвиденная ошибка, что-то пошло не так! Тип ошибки: {error.__class__.__name__}. '
        except Exception as error:
            if error.__class__ in lists_classes:
                pattern = r'\d+'
                status_code = search(pattern, str(error))
                return f'Непредвиденная ошибка, что-то пошло не так! Тип ошибки: {error.__class__.__name__}. ' \
                       f'Текст ошибки: {str(error)[5:]}. Статус кода: {status_code[0]}'
            return f'Непредвиденная ошибка, что-то пошло не так! Тип ошибки: {error.__class__.__name__}.'
    return wrapper