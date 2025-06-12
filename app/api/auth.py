from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.schemas import NewUser, UserOut, UserRole
from app.deps import get_db, get_current_user  # ← get_current_user ещё не нужно здесь
from app.models import User as UserModel, RoleEnum

router = APIRouter(
    prefix="/api/v1/public",
    tags=["public"],
)

@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register",
)
async def register(
    new_user: NewUser,
    db: AsyncSession = Depends(get_db),
):
    # 1) проверяем, что такого username ещё нет
    q = await db.execute(select(UserModel).where(UserModel.username == new_user.name))
    exists = q.scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail="Username already exists")
    # 2) создаём новый объект
    user = UserModel(
        id=uuid4(),
        username=new_user.name,
        password_hash="",            # пока пусто, позже добавите хеш
        api_key=f"key-{uuid4()}",
        role=RoleEnum.USER,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    # 3) возвращаем ORM-объект — Pydantic сам превратит его в UserOut
    return user

# @router.post(
#     "/register",
#     response_model=UserOut,
#     status_code=status.HTTP_200_OK,
#     summary="Register",
#     description=(
#         "Регистрация пользователя в платформе. "
#         "API-ключ из ответа нужно передавать в заголовке "
#         "`Authorization: TOKEN <api_key>`"
#     ),
#     operation_id="register_api_v1_public_register_post",
# )
# async def register(
#     new_user: NewUser,
#     db: AsyncSession = Depends(get_db),
# ):
#     # 1) Проверяем, что имя свободно
#     q = await db.execute(select(User).where(User.username == new_user.name))
#     if q.scalar_one_or_none():
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Имя уже занято",
#         )

#     # 2) Генерируем ключ (в spec — начинается с 'key-')
#     api_key = f"key-{uuid.uuid4()}"

#     # 3) Создаём модель и сохраняем
#     user = User(
#         username=new_user.name,
#         password_hash="", # временный костыль чтобы не было валидации
#         api_key=api_key,
#         role=UserRole.USER,    # по умолчанию USER
#     )
#     db.add(user)
#     await db.commit()
#     await db.refresh(user)

#     # 4) Отдаём обратно весь объект User
#     return UserOut(
#         id=user.id,
#         name=user.username,
#         role=user.role,
#         api_key=user.api_key,
#     )
