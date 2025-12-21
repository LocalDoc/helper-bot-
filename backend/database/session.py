"""Модуль для управления асинхронными сессиями базы данных"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine
)
from typing import AsyncGenerator
from backend.config import settings

database_url = str(settings.DATABASE_URL)

engine: AsyncEngine = create_async_engine(
    database_url,
    echo=settings.DEBUG,  # Логирование SQL-запросов в режиме отладки
    future=True,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Создаем фабрику асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость (dependency) для FastAPI
    Возвращает асинхронную сессию для использования в эндпоинтах
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Инициализация базы данных"""
    from backend.models.database import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("База данных инициализирована")


async def close_db() -> None:
    """Закрытие соединений с базой данных"""
    await engine.dispose()
    print("Соединения с базой данных закрыты")
