from pydantic import BaseModel


class Base(BaseModel):
    pass

class CreateUser(Base):
    name: str
    email: str
    password: str

class CreateTask(Base):
    title: str
    description: str
    status: str
    user_id: int