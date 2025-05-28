from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.settings.config import Settings

setting_db = f"postgresql+asyncpg://{Settings.database_user}:{Settings.database_password}@{Settings.database_host}:{Settings.database_port}/{Settings.database_name}"

engine = create_async_engine(setting_db)
async_session_maker = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


class Base(DeclarativeBase):
    pass
