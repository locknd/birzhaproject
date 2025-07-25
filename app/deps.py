import os
from typing import AsyncGenerator
from uuid import UUID
from fastapi import HTTPException, status, Depends, Header
from app.models import User
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.api.jwt_token import decode_access_token 
# from jose import JWTError

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
    authorization: str = Header(..., alias="Authorization",
                                description="Введите `TOKEN <ваш_api_key>`"),
    db: AsyncSession = Depends(get_db),
) -> UUID:
    prefix = "TOKEN "
    if not authorization.startswith(prefix):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            detail="Missing or wrong token prefix")
    api_key = authorization[len(prefix):].strip()

    user = await db.scalar(
        select(User).where(User.api_key == api_key)
    )
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid API key")

    return user.id
# async def get_current_user(
#     authorization: str = Header(
#         ...,
#         alias="Authorization",
#         description="Введите `TOKEN key-<ваш_api_key>`, например:\n"
#                     "`Authorization: TOKEN key-bee6de4d-7a23-4bb1-a048-523c2ef0ea0c`"
#     ),
#     db: AsyncSession = Depends(get_db),
# ) -> UUIDType:
#     if not authorization:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Missing authorization header"
#         )

#     prefix = "TOKEN key-"
#     if not authorization.startswith(prefix):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authorization format. Expected: TOKEN key-<api_key>"
#         )

#     api_key = authorization[len(prefix):].strip()
#     if not api_key:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Missing API key"
#         )

#     user = await db.scalar(
#         select(User).where(User.api_key == api_key)
#     )
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid API key"
#         )

#     return user.id
# async def get_current_user(
#     authorization: str = Header(
#         ...,
#         alias="Authorization",
#         description="Введите `TOKEN key-<ваш_api_key>`, например:\n"
#                     "`Authorization: TOKEN key-bee6de4d-7a23-4bb1-a048-523c2ef0ea0c`"
#     ),
#     db: AsyncSession = Depends(get_db),
# ) -> UUIDType:
#     if not authorization:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Missing authorization header"
#         )

#     prefix = "TOKEN key-"
#     if not authorization.startswith(prefix):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authorization format. Expected: TOKEN key-<api_key>"
#         )

#     api_key = authorization[len(prefix):].strip()
#     if not api_key:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Missing API key"
#         )

#     user = await db.scalar(
#         select(User).where(User.api_key == api_key)
#     )
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid API key"
#         )

#     return user.id