from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user, get_db
from app.models import User, Instrument, Balance, Order, Transaction
from app.schemas import (
    Instrument as InstrumentSchema,
    UserOut,WithdrawBody,DepositBody,Ok,
)

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


async def get_current_admin(
    user_id: UUID = Depends(get_current_user),  # Получаем user_id из get_current_user
    db: AsyncSession = Depends(get_db),
) -> User:
    # Берём пользователя из БД и проверяем роль
    stmt = select(User).where(User.id == user_id)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    if not user or user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins may call this endpoint"
        )
    return user



    @router.post("/instrument", response_model=Ok, status_code=status.HTTP_201_CREATED)
    async def add_instrument(
        instr: Instrument,
        _admin: User = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db),
    ):
        # Проверка уникальности
        stmt = select(Instrument).where(Instrument.ticker == instr.ticker)
        
        # Дожидаемся выполнения запроса
        result = await db.execute(stmt)
        instrument = result.scalar_one_or_none()

        if instrument:
            raise HTTPException(status_code=409,
                                detail=f"Instrument {instr.ticker} already exists")
        
        # Создаём новый инструмент
        new = Instrument(ticker=instr.ticker, name=instr.name)
        db.add(new)
        await db.commit()
        return Ok()


@router.delete("/instrument/{ticker}", response_model=Ok)
async def delete_instrument(
    ticker: str,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    # Удаляем инструмент (cascade удалит связанные балансы/ордеры/транзакции)
    stmt = delete(Instrument).where(Instrument.ticker == ticker)
    res = await db.execute(stmt)
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Instrument not found")
    await db.commit()
    return Ok()


@router.get("/users", response_model=List[UserOut])
async def list_users(
    _admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User)
    res = await db.execute(stmt)
    users = res.scalars().all()
    return [UserOut.model_validate(u) for u in users]



@router.post("/balance/deposit", response_model=Ok)
async def deposit(
    body: DepositBody,
    _admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    # 1) Проверяем, что пользователь есть
    stmt_u = select(User).where(User.id == body.user_id)
    result_u = await db.execute(stmt_u)
    if not result_u.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="User not found")

    # 2) Проверяем, что инструмент существует и в рублях
    stmt_i = select(Instrument).where(Instrument.ticker == body.ticker)
    result_i = await db.execute(stmt_i)
    inst = result_i.scalar_one_or_none()
    if not inst:
        raise HTTPException(status_code=404, detail="Instrument not found")
    if inst.currency != "RUB":
        raise HTTPException(
            status_code=400,
            detail=f"Instrument {body.ticker} is not traded in RUB"
        )

    # 3) Обновляем или создаём запись баланса
    stmt_b = select(Balance).where(
        Balance.user_id == body.user_id,
        Balance.ticker == body.ticker
    )
    result_b = await db.execute(stmt_b)
    balance = result_b.scalar_one_or_none()

    if balance:
        new_amount = balance.amount + body.amount
        await db.execute(
            update(Balance)
            .where(Balance.id == balance.id)
            .values(amount=new_amount)
        )
    else:
        db.add(Balance(
            user_id=body.user_id,
            ticker=body.ticker,
            amount=body.amount
        ))

    await db.commit()
    return Ok()


@router.post("/balance/withdraw", response_model=Ok)
async def withdraw(
    body: WithdrawBody,
    _admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    # 1) Проверяем баланс
    stmt_b = select(Balance).where(
        Balance.user_id == body.user_id,
        Balance.ticker == body.ticker
    )
    result_b = await db.execute(stmt_b)
    balance = result_b.scalar_one_or_none()
    if not balance:
        raise HTTPException(status_code=404, detail="Balance not found")
    if balance.amount < body.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # 2) Списываем
    await db.execute(
        update(Balance)
        .where(Balance.id == balance.id)
        .values(amount=balance.amount - body.amount)
    )
    await db.commit()
    return Ok()