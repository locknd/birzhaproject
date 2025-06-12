import os
from typing import AsyncGenerator
from uuid import UUID

from fastapi import Header, HTTPException, status

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.api.public import users        # in-memory users store
# from app.models import User             # SQLAlchemy модель пользователя ЗАГЛУШКА ((замените in-memory-хранилище на настоящий запрос к БД (тогда и понадобятся User + UserOut)))
# from app.schemas.auth import UserOut    # Pydantic схема пользователя

# Взято из переменных окружения (или .env через python-dotenv)
DATABASE_URL = os.getenv("DATABASE_URL")

# 1) Создаём асинхронный движок
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # для логирования SQL-запросов
)

# 2) Конфигурируем фабрику сессий
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 3) Депенденси, отдающий сессию в каждый запрос и корректно её закрывающий
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# 4) Депенденси для получения текущего пользователя по API-ключу
async def get_current_user(
    api_key: str = Header(None, alias="Authorization")
) -> UUID:
    """
    Извлекает текущего пользователя по API-ключу из заголовка Authorization.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key"
        )
    # ищем в in-memory store из public.py
    for user in users.values():
        if user.api_key == api_key:
            return user.id
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key"
    )