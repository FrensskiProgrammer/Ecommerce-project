from pydantic import BaseModel


class Base(BaseModel):
    pass


class CreateUser(Base):
    """Схема для модели User"""

    name: str
    email: str
    password: str


class CreateTask(Base):
    """Схема для модели Task"""

    title: str
    description: str
    status: str
    user_id: int
