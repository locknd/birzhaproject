from fastapi import APIRouter, HTTPException, Query, status
from typing import List
from uuid import uuid4
from app.models import User as UserModel, RoleEnum
from app.schemas import (
    NewUser, UserOut, Instrument,
    L2OrderBook, Transaction
)
# from app.deps import get_current_user, get_db  # в будущем замените логику

router = APIRouter(
    prefix="/api/v1/public",
    tags=["public"]
)

# In-memory хранилища
users: dict[uuid4, UserModel] = {}

instruments = {
    "MEMCOIN": Instrument(name="Memory Coin", ticker="MEMCOIN"),
    "DODGE": Instrument(name="Dodge Coin", ticker="DODGE")
}
orderbooks = {t: L2OrderBook(bid_levels=[], ask_levels=[]) for t in instruments}
transactions = {t: [] for t in instruments}

router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
async def register(user: NewUser):
    # 1) Сначала создаём user_id и api_key
    user_id = uuid4()
    api_key = f"key-{uuid4()}"

    # 2) Затем передаём уже готовые переменные в конструктор ORM-модели
    new_user = UserModel(
        id=user_id,
        username=user.name,
        password_hash="",            # пока пусто
        api_key=api_key,
        role=RoleEnum[user.role],    # RoleEnum.USER или RoleEnum.ADMIN
    )

    users[user_id] = new_user

    # 3) Возвращаем ORM-объект целиком: Pydantic UserOut из него «прочитает» все поля
    return new_user

@router.get("/instrument", response_model=List[Instrument])
async def list_instruments():
    return list(instruments.values())

@router.get("/orderbook/{ticker}", response_model=L2OrderBook)
async def get_orderbook(
    ticker: str,
    limit: int = Query(10, le=25)
):
    if ticker not in orderbooks:
        raise HTTPException(status_code=404, detail="Ticker not found")
    ob = orderbooks[ticker]
    return L2OrderBook(
        bid_levels=ob.bid_levels[:limit],
        ask_levels=ob.ask_levels[:limit]
    )

@router.get("/transactions/{ticker}", response_model=List[Transaction])
async def get_transactions(
    ticker: str,
    limit: int = Query(10, le=100)
):
    if ticker not in transactions:
        raise HTTPException(status_code=404, detail="Ticker not found")
    return transactions[ticker][-limit:]