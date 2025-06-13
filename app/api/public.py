from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from sqlalchemy import select, func, desc, asc, or_

# SQLAlchemy-модель
from app.models import Instrument as InstrumentModel, Transaction as TransactionModel
# Pydantic-схема
from app.schemas import Instrument as InstrumentSchema, Transaction as TransactionSchema

from app.deps import get_db
from app.models import User, Order
from app.schemas import (
    NewUser,
    UserOut,
    L2OrderBook,
    Level
)


router = APIRouter(
    prefix="/api/v1/public",
    tags=["Public"],
)

# @router.post(
#     "/register",
#     response_model=UserOut,
#     status_code=status.HTTP_201_CREATED,
# )
# async def register(
#     user: NewUser,
#     db: AsyncSession = Depends(get_db),
# ):
#     """
#     Регистрация пользователя в платформе. Обязательна для совершения сделок.
#     api_key, полученный из этого метода, следует передавать в другие через заголовок Authorization.
#     """
#     user_id = uuid4()
#     api_key = f"key-{uuid4()}"
#     new_user = User(
#         id=user_id,
#         username=user.name,
#         password_hash="",  # пока заглушка
#         api_key=api_key,
#         role=user.role,
#     )

#     db.add(new_user)
#     try:
#         await db.commit()
#     except IntegrityError:
#         await db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="Username already exists"
#         )

#     await db.refresh(new_user)
#     return new_user
@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False
)
async def register(
    user: NewUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Регистрация пользователя в платформе. Обязательна для совершения сделок.
    api_key, полученный из этого метода следует передавать в другие через заголовок Authorization.
    """
    # 1) Генерируем ID и ключ
    user_id = uuid4()
    api_key = str(uuid4())

    # 2) Строим ORM-объект
    new_user = User(
        id=user_id,
        username=user.name,
        password_hash="",        # пока пусто
        api_key=api_key,
        role=user.role,          # Pydantic Literal["USER","ADMIN"] -> Enum автоматически
    )

    # 3) Сохраняем
    db.add(new_user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )

    # 4) Обновляем из БД, чтобы подтянулись все поля
    await db.refresh(new_user)

    # 5) Возвращаем Pydantic-модель
    return new_user


@router.get(
    "/instrument",
    response_model=List[InstrumentSchema],
    status_code=status.HTTP_200_OK,
)
async def list_instruments(
    db: AsyncSession = Depends(get_db),
):
    """
    Список доступных инструментов (статус ACTIVE).
    """
    stmt = select(InstrumentModel).where(
        InstrumentModel.status == InstrumentModel.status.default.arg
    )
    result = await db.execute(stmt)
    instruments = result.scalars().all()

    return [
        InstrumentSchema(
            name=inst.name,
            ticker=inst.ticker
        )
        for inst in instruments
    ]





@router.get(
    "/orderbook/{ticker}",
    response_model=L2OrderBook,
    status_code=status.HTTP_200_OK,
)
async def get_orderbook(
    ticker: str = Path(..., description="Тикер инструмента"),
    limit: int = Query(10, ge=1, le=100, description="Сколько топ-уровней вернуть"),
    db: AsyncSession = Depends(get_db),
):
    """
    Строит стакан из незакрытых заявок в БД:
      - bid_levels: все BUY-заявки
      - ask_levels: все SELL-заявки
    Группировка по цене, суммирование qty, сортировка.
    """
    # какие статусы считаем «живыми»
    alive = [Order.status == "NEW", Order.status == "PARTIALLY_EXECUTED"]

    # 1) BIDS: группируем BUY, по убыванию цены
    stmt_bids = (
        select(
            Order.price.label("price"),
            func.sum(Order.quantity).label("qty")
        )
        .where(
            Order.ticker == ticker,
            Order.side == "BUY",
            or_(*alive)
        )
        .group_by(Order.price)
        .order_by(desc(Order.price))
        .limit(limit)
    )
    bids = await db.execute(stmt_bids)
    bid_levels = [
        Level(price=int(row.price), qty=int(row.qty))
        for row in bids.fetchall()
    ]

    # 2) ASKS: группируем SELL, по возрастанию цены
    stmt_asks = (
        select(
            Order.price.label("price"),
            func.sum(Order.quantity).label("qty")
        )
        .where(
            Order.ticker == ticker,
            Order.side == "SELL",
            or_(*alive)
        )
        .group_by(Order.price)
        .order_by(asc(Order.price))
        .limit(limit)
    )
    asks = await db.execute(stmt_asks)
    ask_levels = [
        Level(price=int(row.price), qty=int(row.qty))
        for row in asks.fetchall()
    ]

    if not bid_levels and not ask_levels:
        raise HTTPException(status_code=404, detail=f"No active orders for {ticker}")

    return L2OrderBook(bid_levels=bid_levels, ask_levels=ask_levels)

@router.get(
    "/transactions/{ticker}",
    response_model=List[TransactionSchema],
    status_code=status.HTTP_200_OK,
)
async def get_transaction_history(
    ticker: str = Path(..., description="Тикер инструмента"),
    limit: int = Query(10, ge=1, le=1000, description="Максимум записей"),
    db: AsyncSession = Depends(get_db),
):
    """
    История последних сделок по инструменту.
    """
    stmt = (
        select(TransactionModel)  # Используем SQLAlchemy модель
        .where(TransactionModel.ticker == ticker)
        .order_by(TransactionModel.timestamp.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    trades = result.scalars().all()

    # Преобразуем данные в Pydantic схемы для ответа
    return [
        TransactionSchema(
            ticker=t.ticker,
            amount=int(t.quantity),
            price=int(t.price),
            timestamp=t.timestamp,
        )
        for t in trades
    ]