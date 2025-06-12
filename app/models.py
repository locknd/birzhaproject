import enum
import uuid
import datetime
from datetime import timezone

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Numeric,
    ForeignKey,
    Enum as SQLEnum  # aliased to avoid conflict with Python's enum.Enum
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# ===================== ENUM’ы =====================
class RoleEnum(str, enum.Enum):
    USER  = "USER"
    ADMIN = "ADMIN"

class InstrumentStatusEnum(str, enum.Enum):
    ACTIVE   = "ACTIVE"
    DELISTED = "DELISTED"

class OrderSideEnum(str, enum.Enum):
    BUY  = "BUY"
    SELL = "SELL"

class OrderStatusEnum(str, enum.Enum):
    NEW                 = "NEW"
    PARTIALLY_EXECUTED  = "PARTIALLY_EXECUTED"
    EXECUTED            = "EXECUTED"
    CANCELLED           = "CANCELLED"

# ===================== Таблицы =====================
class User(Base):
    __tablename__ = "users"

    id = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False
    )
    username      = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    api_key       = Column(String, unique=True, nullable=False, index=True)
    role          = Column(
        SQLEnum(RoleEnum, name="userrole", native_enum=True),
        default=RoleEnum.USER,
        nullable=False
    )
    created_at    = Column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(timezone.utc),
        nullable=False
    )

    balances = relationship("Balance", back_populates="user", cascade="all, delete-orphan")
    orders   = relationship("Order",   back_populates="user", cascade="all, delete-orphan")


class Instrument(Base):
    __tablename__ = "instruments"

    ticker  = Column(String, primary_key=True, index=True, nullable=False)
    name    = Column(String, nullable=False)
    status  = Column(
        SQLEnum(InstrumentStatusEnum, name="instrumentstatusenum", native_enum=True),
        default=InstrumentStatusEnum.ACTIVE,
        nullable=False
    )

    balances     = relationship("Balance",     back_populates="instrument", cascade="all, delete-orphan")
    orders       = relationship("Order",       back_populates="instrument", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="instrument", cascade="all, delete-orphan")


class Balance(Base):
    __tablename__ = "balances"

    id      = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False
    )
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    ticker  = Column(String, ForeignKey("instruments.ticker"), nullable=False)
    amount  = Column(Numeric(20, 8), default=0, nullable=False)

    user       = relationship("User",       back_populates="balances")
    instrument = relationship("Instrument", back_populates="balances")


class Order(Base):
    __tablename__ = "orders"

    id          = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False
    )
    user_id     = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    ticker      = Column(String, ForeignKey("instruments.ticker"), nullable=False)
    side        = Column(SQLEnum(OrderSideEnum, name="ordersideenum", native_enum=True), nullable=False)
    quantity    = Column(Numeric(20, 8), nullable=False)
    price       = Column(Numeric(20, 8), nullable=True)
    status      = Column(SQLEnum(OrderStatusEnum, name="orderstatusenum", native_enum=True), default=OrderStatusEnum.NEW, nullable=False)
    filled_qty  = Column(Numeric(20, 8), default=0, nullable=False)
    created_at  = Column(DateTime(timezone=True), default=lambda: datetime.datetime.now(timezone.utc), nullable=False)

    user            = relationship("User",       back_populates="orders")
    instrument      = relationship("Instrument", back_populates="orders")
    buy_transactions  = relationship("Transaction", back_populates="buy_order",  foreign_keys="[Transaction.buy_order_id]")
    sell_transactions = relationship("Transaction", back_populates="sell_order", foreign_keys="[Transaction.sell_order_id]")


class Transaction(Base):
    __tablename__ = "transactions"

    id            = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False
    )
    buy_order_id  = Column(PG_UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    sell_order_id = Column(PG_UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    ticker        = Column(String, ForeignKey("instruments.ticker"), nullable=False)
    quantity      = Column(Numeric(20, 8), nullable=False)
    price         = Column(Numeric(20, 8), nullable=False)
    timestamp     = Column(DateTime(timezone=True), default=lambda: datetime.datetime.now(timezone.utc), nullable=False)

    buy_order  = relationship("Order", back_populates="buy_transactions",  foreign_keys=[buy_order_id])
    sell_order = relationship("Order", back_populates="sell_transactions", foreign_keys=[sell_order_id])
    instrument = relationship("Instrument", back_populates="transactions")