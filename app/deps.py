import os
from typing import AsyncGenerator
from uuid import UUID
from fastapi import HTTPException, status, Depends
from app.models import User
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from fastapi.security import APIKeyHeader

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

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

async def get_current_user(
    api_key: str = Depends(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> UUID:
    """
    Извлекает текущего пользователя по API-ключу из заголовка Authorization,
    ищет его в таблице users и возвращает user.id.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key"
        )

    # Ищем в БД
    result = await db.scalar(
        select(User).where(User.api_key == api_key)
    )
    user: User | None = result  # type: ignore

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    return user.id

