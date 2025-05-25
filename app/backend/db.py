from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.settings.config import settings

setting_db = f'postgresql+asyncpg://{settings.database_user}:{settings.database_password}@{settings.database_host}:{settings.database_port}/{settings.database_name}'

engine = create_async_engine(f'postgresql+asyncpg://technosfera:T42ASlz08l@localhost:5432/database_name')
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass