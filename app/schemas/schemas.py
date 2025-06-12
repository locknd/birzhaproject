from enum import Enum
from uuid import UUID
from datetime import datetime
from typing import List, Dict

from pydantic import BaseModel, Field, field_validator, ConfigDict

# === ENUM’ы ===
class UserRole(str, Enum):
    USER  = "USER"
    ADMIN = "ADMIN"

class OrderStatus(str, Enum):
    NEW                  = "NEW"
    EXECUTED             = "EXECUTED"
    PARTIALLY_EXECUTED   = "PARTIALLY_EXECUTED"
    CANCELLED            = "CANCELLED"

class Direction(str, Enum):
    BUY  = "BUY"
    SELL = "SELL"

# === User schemas ===
class NewUser(BaseModel):
    name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Уникальное имя пользователя"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"name": "ivan_ivanov"}
        }
    )

class UserOut(BaseModel):
    id:      UUID     = Field(..., description="UUID пользователя")
    name:    str      = Field(..., alias="username", description="Имя пользователя")
    role:    UserRole = Field(..., description="Роль пользователя")
    api_key: str      = Field(..., description="API-ключ")

    model_config = ConfigDict(
        from_attributes=True,      # <-- tell Pydantic читать ваши атрибуты
        populate_by_name=True,     # <-- чтобы Pydantic знал, что `name` брать из `username`
        json_schema_extra={
            "example": {
                "id":      "35b0884d-9a1d-47b0-91c7-eecf0ca56bc8",
                "name":    "ivan_ivanov",
                "role":    "USER",
                "api_key": "key-550e8400-e29b-41d4-a716-446655440000"
            }
        }
    )

    @field_validator("role", mode="before")
    def _upper_role(cls, v):
        return v.upper() if isinstance(v, str) else v

# === Instrument & OrderBook schemas ===
class Instrument(BaseModel):
    name:   str
    ticker: str

class Level(BaseModel):
    price: int
    qty:   int

class L2OrderBook(BaseModel):
    bid_levels: List[Level]
    ask_levels: List[Level]

# === Transaction schema ===
class Transaction(BaseModel):
    ticker:    str
    amount:    int
    price:     int
    timestamp: datetime

# === Order schemas ===
class LimitOrderBody(BaseModel):
    direction: Direction
    ticker:    str
    qty:       int
    price:     int

class MarketOrderBody(BaseModel):
    direction: Direction
    ticker:    str
    qty:       int

class LimitOrder(BaseModel):
    id:        UUID
    status:    OrderStatus
    user_id:   UUID
    timestamp: datetime
    body:      LimitOrderBody
    filled:    int = 0

class MarketOrder(BaseModel):
    id:        UUID
    status:    OrderStatus
    user_id:   UUID
    timestamp: datetime
    body:      MarketOrderBody

class CreateOrderResponse(BaseModel):
    success:  bool = True
    order_id: UUID

class Ok(BaseModel):
    success: bool = True

# === Balance schemas ===
class BalanceOut(BaseModel):
    ticker: str   = Field(..., description="Инструмент")
    amount: float = Field(..., description="Количество инструмента")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"MEMCOIN": 100.5, "DODGE": 50.0}
        }
    )