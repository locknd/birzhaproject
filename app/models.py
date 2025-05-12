from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Numeric
from sqlalchemy.orm import relationship, declarative_base
import enum
import datetime

Base = declarative_base()

# ===================== ENUM’ы =====================

class RoleEnum(enum.Enum):
    USER = "user"
    ADMIN = "admin"

class InstrumentStatusEnum(enum.Enum):
    ACTIVE = "active"
    DELISTED = "delisted"

class OrderSideEnum(enum.Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatusEnum(enum.Enum):
    NEW = "new"
    PARTIALLY_EXECUTED = "partially_executed"
    EXECUTED = "executed"
    CANCELLED = "cancelled"

# ===================== МОДЕЛИ =====================

class User(Base):
    __tablename__ = "users"

    id           = Column(Integer, primary_key=True, index=True)
    username     = Column(String, unique=True, nullable=False, index=True)
    password_hash= Column(String, nullable=False)
    api_key      = Column(String, unique=True, nullable=False, index=True)
    role         = Column(Enum(RoleEnum), default=RoleEnum.USER, nullable=False)
    created_at   = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    balances = relationship("Balance", back_populates="user", cascade="all, delete-orphan")
    orders   = relationship("Order",   back_populates="user", cascade="all, delete-orphan")


class Instrument(Base):
    __tablename__ = "instruments"

    ticker  = Column(String, primary_key=True, index=True)
    name    = Column(String, nullable=False)
    status  = Column(Enum(InstrumentStatusEnum), default=InstrumentStatusEnum.ACTIVE, nullable=False)

    balances     = relationship("Balance",     back_populates="instrument", cascade="all, delete-orphan")
    orders       = relationship("Order",       back_populates="instrument", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="instrument", cascade="all, delete-orphan")


class Balance(Base):
    __tablename__ = "balances"

    id      = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ticker  = Column(String,  ForeignKey("instruments.ticker"), nullable=False)
    amount  = Column(Numeric(20, 8), default=0, nullable=False)

    user       = relationship("User",       back_populates="balances")
    instrument = relationship("Instrument", back_populates="balances")


class Order(Base):
    __tablename__ = "orders"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    ticker     = Column(String,  ForeignKey("instruments.ticker"), nullable=False)
    side       = Column(Enum(OrderSideEnum), nullable=False)
    qty        = Column(Numeric(20, 8), nullable=False)
    price      = Column(Numeric(20, 8), nullable=True)  # NULL для market-заявок
    status     = Column(Enum(OrderStatusEnum), default=OrderStatusEnum.NEW, nullable=False)
    filled_qty = Column(Numeric(20, 8), default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    user      = relationship("User",       back_populates="orders")
    instrument= relationship("Instrument", back_populates="orders")
    buy_transactions  = relationship(
        "Transaction",
        back_populates="buy_order",
        foreign_keys="[Transaction.buy_order_id]",
    )
    sell_transactions = relationship(
        "Transaction",
        back_populates="sell_order",
        foreign_keys="[Transaction.sell_order_id]",
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id            = Column(Integer, primary_key=True, index=True)
    buy_order_id  = Column(Integer, ForeignKey("orders.id"), nullable=False)
    sell_order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    ticker        = Column(String,  ForeignKey("instruments.ticker"), nullable=False)
    qty           = Column(Numeric(20, 8), nullable=False)
    price         = Column(Numeric(20, 8), nullable=False)
    timestamp     = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    buy_order  = relationship(
        "Order",
        back_populates="buy_transactions",
        foreign_keys=[buy_order_id],
    )
    sell_order = relationship(
        "Order",
        back_populates="sell_transactions",
        foreign_keys=[sell_order_id],
    )
    instrument = relationship("Instrument", back_populates="transactions")