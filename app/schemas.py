from pydantic import BaseModel


class CreateUser(BaseModel):
    name: str
    email: str
    password: str

class CreateTask(BaseModel):
    title: str
    description: str
    status: str
    user_id: int