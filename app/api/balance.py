from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_current_user
from app.models import Balance, Instrument
from app.schemas import BalanceOut, DepositBody, WithdrawBody, Ok

router = APIRouter(
    prefix="/api/v1/balance",
    tags=["Balance"],
)

@router.get(
    "/",
    response_model=List[BalanceOut],
    status_code=status.HTTP_200_OK,
)
async def get_balances(
    current_user: UUID     = Depends(get_current_user),
    db: AsyncSession       = Depends(get_db),
):
    stmt = select(Balance).where(Balance.user_id == current_user)
    res  = await db.execute(stmt)
    rows = res.scalars().all()
    return [BalanceOut(ticker=r.ticker, amount=int(r.amount)) for r in rows]


@router.post(
    "/deposit",
    response_model=Ok,
    status_code=status.HTTP_200_OK,
)
async def deposit(
    body: DepositBody,
    current_user: UUID     = Depends(get_current_user),
    db: AsyncSession       = Depends(get_db),
):
    stmt_i = select(Instrument).where(Instrument.ticker == body.ticker)
    inst   = (await db.execute(stmt_i)).scalar_one_or_none()
    if not inst:
        raise HTTPException(404, "Instrument not found")
    if inst.currency != "RUB":
        raise HTTPException(400, "Instrument is not traded in RUB")

    stmt_b = select(Balance).where(
        Balance.user_id == current_user,
        Balance.ticker  == body.ticker
    )
    bal = (await db.execute(stmt_b)).scalar_one_or_none()

    if bal:
        await db.execute(
            update(Balance)
            .where(Balance.id == bal.id)
            .values(amount=bal.amount + body.amount)
        )
    else:
        db.add(Balance(
            user_id=current_user,
            ticker=body.ticker,
            amount=body.amount
        ))

    await db.commit()
    return Ok()


@router.post(
    "/withdraw",
    response_model=Ok,
    status_code=status.HTTP_200_OK,
)
async def withdraw(
    body: WithdrawBody,
    current_user: UUID     = Depends(get_current_user),
    db: AsyncSession       = Depends(get_db),
):
    stmt_b = select(Balance).where(
        Balance.user_id == current_user,
        Balance.ticker  == body.ticker
    )
    bal = (await db.execute(stmt_b)).scalar_one_or_none()
    if not bal:
        raise HTTPException(404, "Balance not found")
    if bal.amount < body.amount:
        raise HTTPException(400, "Insufficient funds")

    await db.execute(
        update(Balance)
        .where(Balance.id == bal.id)
        .values(amount=bal.amount - body.amount)
    )
    await db.commit()
    return Ok()