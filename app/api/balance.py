from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_current_user
from app.models import Balance  # SQLAlchemy модель баланса
# from app.schemas import BalanceOut  # Pydantic схема для баланса

router = APIRouter(
    prefix="/api/v1/balance",
    tags=["balance"]
)

@router.get(
    "/",
    response_model=Dict[str, float],
    status_code=status.HTTP_200_OK
)
async def get_balances(
    db: AsyncSession = Depends(get_db),
    current_user: UUID = Depends(get_current_user)
) -> Dict[str, float]:
    """
    Возвращает карту {ticker: amount} для текущего пользователя из БД.
    """
    # Запрос всех записей баланса пользователя
    result = await db.execute(
        select(Balance).where(Balance.user_id == current_user)
    )
    balances = result.scalars().all()
    # Формируем словарь ticker -> amount
    return {b.instrument_ticker: float(b.amount) for b in balances}