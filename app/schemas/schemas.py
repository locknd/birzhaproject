import re
from enum import Enum
from uuid import UUID
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict

# === ENUM'ы ===
class UserRole(str, Enum):
    USER  = "USER"
    ADMIN = "ADMIN"

class OrderStatus(str, Enum):
    NEW                 = "NEW"
    EXECUTED            = "EXECUTED"
    PARTIALLY_EXECUTED  = "PARTIALLY_EXECUTED"
    CANCELLED           = "CANCELLED"

class Direction(str, Enum):
    BUY  = "BUY"
    SELL = "SELL"

# Общий валидатор для тикера
@field_validator('*', mode='before')
def _validate_ticker(cls, v, field):
    if field.name in ('ticker',):
        if not re.match(r"^[A-Z]+RUB$", v):
            raise ValueError("Ticker must end with 'RUB'")
    return v

# === User schemas ===
class NewUser(BaseModel):
    name: str = Field(..., min_length=3, description="Уникальное имя пользователя")
    role: Literal["USER", "ADMIN"] = Field("USER", description="Роль пользователя")

    model_config = ConfigDict(
        json_schema_extra={"example": {"name": "ivan_ivanov", "role": "USER"}}
    )

class UserOut(BaseModel):
    id: UUID = Field(..., description="UUID пользователя", format="uuid4")
    name: str | None = Field(default=None, alias="username", description="Имя пользователя")
    role: Optional[UserRole] = Field(default=UserRole.USER, description="Роль пользователя")
    api_key: str = Field(..., description="API-ключ")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={"example": {"id": "35b0884d-9a1d-47b0-91c7-eecf0ca56bc8", "name": "ivan_ivanov", "role": "USER", "api_key": "550e8400-e29b-41d4-a716-446655440000"}}
    )

    @field_validator("role", mode="before")
    def _upper_role(cls, v):
        return v.upper() if isinstance(v, str) else v

# === Instrument & OrderBook schemas ===
class Instrument(BaseModel):
    name: str
    ticker: str
    currency: Literal["RUB"] = Field("RUB", description="Валюта расчёта — всегда RUB")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"example": {"name": "Bitcoin / RUB", "ticker": "BTCRUB", "currency": "RUB"}}
    )

class Level(BaseModel):
    price: int
    qty: int

class L2OrderBook(BaseModel):
    bid_levels: List[Level]
    ask_levels: List[Level]

class Transaction(BaseModel):
    ticker: str
    amount: int
    price: int
    timestamp: datetime

# === Order schemas ===
class LimitOrderBody(BaseModel):
    direction: Direction = Field(..., description="Направление ордера")
    ticker: str = Field(..., description="Тикер инструмента — должен заканчиваться на RUB")
    qty: int = Field(..., ge=1, description="Количество лотов — минимум 1")
    price: int = Field(..., gt=0, description="Цена за лот — > 0")

    model_config = ConfigDict(
        json_schema_extra={"example": {"direction": "BUY", "ticker": "BTCRUB", "qty": 1, "price": 500000}}
    )

class MarketOrderBody(BaseModel):
    direction: Direction = Field(..., description="Направление ордера")
    ticker: str = Field(..., description="Тикер инструмента — должен заканчиваться на RUB")
    qty: int = Field(..., ge=1, description="Количество лотов — минимум 1")

    model_config = ConfigDict(
        json_schema_extra={"example": {"direction": "SELL", "ticker": "BTCRUB", "qty": 2}}
    )

class LimitOrder(BaseModel):
    id: UUID = Field(..., format="uuid4")
    status: OrderStatus
    user_id: UUID = Field(..., format="uuid4")
    timestamp: datetime
    body: LimitOrderBody
    filled: int = 0

class MarketOrder(BaseModel):
    id: UUID = Field(..., format="uuid4")
    status: OrderStatus
    user_id: UUID = Field(..., format="uuid4")
    timestamp: datetime
    body: MarketOrderBody

class CreateOrderResponse(BaseModel):
    success: bool = True
    order_id: UUID = Field(..., format="uuid4")

class Ok(BaseModel):
    success: bool = True

# === Balance schemas ===
class BalanceOut(BaseModel):
    ticker: str = Field(..., description="Инструмент")
    amount: float = Field(..., description="Количество инструмента")

    model_config = ConfigDict(
        json_schema_extra={"example": {"BTCRUB": 1000.0, "ETHRUB": 5.0}}
    )

# === Admin BalanceChange schemas ===
class DepositBody(BaseModel):
    user_id: UUID = Field(..., description="UUID пользователя", format="uuid")
    ticker: str = Field(..., description="Тикер инструмента — должен заканчиваться на RUB")
    amount: int = Field(..., ge=1, description="Сумма в рублях (целое число)")
    currency: Literal["RUB"] = Field("RUB", description="Валюта расчёта — всегда RUB")

    model_config = ConfigDict(
        json_schema_extra={"example": {"user_id": "35b0884d-9a1d-47b0-91c7-eecf0ca56bc8", "ticker": "BTCRUB", "amount": 10000, "currency": "RUB"}}
    )

    @field_validator("currency", mode="before")
    def _validate_deposit_currency(cls, v):
        if v != "RUB":
            raise ValueError("currency must be 'RUB'")
        return v

class WithdrawBody(DepositBody):
    pass
