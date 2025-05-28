from fastapi import HTTPException
from fastapi import status

class NotFoundUser(HTTPException):
    def __init__(self):
        super().__init__(detail='User not found!', status_code=404)

class DeleteUser(HTTPException):
    def __init__(self):
        super().__init__(detail="You cannot delete someone else's user", status_code=400)

class InvalidName(HTTPException):
    def __init__(self):
        super().__init__(detail='Invalid name or already in use', status_code=403)

class InvalidEmail(HTTPException):
    def __init__(self):
        super().__init__(detail='Invalid email or already in use', status_code=403)

class InvalidPasswd(HTTPException):
    def __init__(self):
        super().__init__(detail='Invalid password', status_code=403)

class UserNotAutorized(HTTPException):
    def __init__(self):
        super().__init__(detail='Could not validate user', status_code=401)
        
class NoAccesToken(HTTPException):
    def __init__(self):
        super().__init__(detail='No access token supplied', status_code=400)

class InvalidToken(HTTPException):
    def __init__(self):
        super().__init__(detail='Invalid token format', status_code=400)

class TokenExpired(HTTPException):
    def __init__(self):
        super().__init__(detail='Token expired!', status_code=401)
        
class TaskNotFound(HTTPException):
    def __init__(self):
        super().__init__(detail='Task not found!', status_code=404)
        
class InvalidTitleTask(HTTPException):
    def __init__(self):
        super().__init__(detail='This name already exists or the id was not found or invalid', status_code=403)
        
class InvalidDescTask(HTTPException):
    def __init__(self):
        super().__init__(detail='Invalid description', status_code=403)
        
class InvalidStatusTask(HTTPException):
    def __init__(self):
        super().__init__(detail='Invalid status', status_code=403)

class IntegError(HTTPException):
    def __init__(self):
        super().__init__(detail='Error', status_code=403)
        
class NoUseTask(HTTPException):
    def __init__(self):
        super().__init__(detail='This item does not belong to you and you do not have access to it', status_code=404)
