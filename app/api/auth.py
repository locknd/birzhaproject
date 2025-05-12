from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.schemas.auth import NewUser, UserOut, UserRole
from app.models import User
from app.deps import get_db

router = APIRouter(
    prefix="/api/v1/public",
    tags=["public"],
)

@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Register",
    description=(
        "Регистрация пользователя в платформе. "
        "API-ключ из ответа нужно передавать в заголовке "
        "`Authorization: TOKEN <api_key>`"
    ),
    operation_id="register_api_v1_public_register_post",
)
async def register(
    new_user: NewUser,
    db: AsyncSession = Depends(get_db),
):
    # 1) Проверяем, что имя свободно
    q = await db.execute(select(User).where(User.username == new_user.name))
    if q.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Имя уже занято",
        )

    # 2) Генерируем ключ (в spec — начинается с 'key-')
    api_key = f"key-{uuid.uuid4()}"

    # 3) Создаём модель и сохраняем
    user = User(
        username=new_user.name,
        password_hash="", # временный костыль чтобы не было валидации
        api_key=api_key,
        role=UserRole.USER,    # по умолчанию USER
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 4) Отдаём обратно весь объект User
    return UserOut(
        id=user.id,
        name=user.username,
        role=user.role,
        api_key=user.api_key,
    )
