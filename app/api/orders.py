from uuid import uuid4, UUID
from datetime import datetime, timezone
from typing import Union, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user, get_db
from app.models import Order, Instrument
from app.schemas import (
    LimitOrderBody,
    MarketOrderBody,
    LimitOrder,
    MarketOrder,
    CreateOrderResponse,
    OrderStatus,
    Ok,
)

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])


@router.post(
    "/",
    response_model=CreateOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    body: Union[LimitOrderBody, MarketOrderBody],
    current_user: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Проверяем, что инструмент существует
    stmt_inst = select(Instrument).where(Instrument.ticker == body.ticker)
    res_inst = await db.execute(stmt_inst)
    inst = res_inst.scalar_one_or_none()
    if not inst:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Instrument '{body.ticker}' not found"
        )

    # Создаём заявку
    order_id = uuid4()
    now = datetime.now(timezone.utc)

    # Для рыночного ордера цена будет подтягиваться из базы данных
    if isinstance(body, MarketOrderBody):
        price = inst.current_price  # Цена для рыночного ордера
    else:
        price = body.price  # Для лимитного ордера цена передается в запросе

    o = Order(
        id=order_id,
        user_id=current_user,
        ticker=body.ticker,
        side=body.direction,
        quantity=body.qty,
        filled_qty=0,
        status=OrderStatus.NEW,
        created_at=now,
        price=price,
    )

    db.add(o)
    await db.commit()
    await db.refresh(o)

    return CreateOrderResponse(order_id=order_id)


@router.get(
    "/",
    response_model=List[Union[LimitOrder, MarketOrder]],
    status_code=status.HTTP_200_OK,
)
async def list_orders(
    current_user: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Order).where(Order.user_id == current_user)
    res = await db.execute(stmt)
    rows = res.scalars().all()

    result: List[Union[LimitOrder, MarketOrder]] = []
    for o in rows:
        if o.price is not None:
            body = LimitOrderBody(
                direction=o.side, ticker=o.ticker, qty=int(o.quantity), price=int(o.price)
            )
            dto = LimitOrder(
                id=o.id,
                status=o.status,
                user_id=o.user_id,
                timestamp=o.created_at,
                body=body,
                filled=int(o.filled_qty),
            )
        else:
            body = MarketOrderBody(
                direction=o.side, ticker=o.ticker, qty=int(o.quantity)
            )
            dto = MarketOrder(
                id=o.id,
                status=o.status,
                user_id=o.user_id,
                timestamp=o.created_at,
                body=body,
            )
        result.append(dto)

    return result


@router.get(
    "/{order_id}",
    response_model=Union[LimitOrder, MarketOrder],
    status_code=status.HTTP_200_OK,
)
async def get_order(
    order_id: UUID,
    current_user: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Order).where(
        Order.id == order_id,
        Order.user_id == current_user,
    )
    res = await db.execute(stmt)
    o = res.scalar_one_or_none()
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")

    if o.price is not None:
        body = LimitOrderBody(
            direction=o.side, ticker=o.ticker, qty=int(o.quantity), price=int(o.price)
        )
        return LimitOrder(
            id=o.id,
            status=o.status,
            user_id=o.user_id,
            timestamp=o.created_at,
            body=body,
            filled=int(o.filled_qty),
        )
    else:
        body = MarketOrderBody(
            direction=o.side, ticker=o.ticker, qty=int(o.quantity)
        )
        return MarketOrder(
            id=o.id,
            status=o.status,
            user_id=o.user_id,
            timestamp=o.created_at,
            body=body,
        )


@router.delete(
    "/{order_id}",
    response_model=Ok,
    status_code=status.HTTP_200_OK,
)
async def cancel_order(
    order_id: UUID,
    current_user: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Order).where(
        Order.id == order_id,
        Order.user_id == current_user,
        Order.status == OrderStatus.NEW,
    )
    res = await db.execute(stmt)
    o = res.scalar_one_or_none()
    if not o:
        raise HTTPException(status_code=404, detail="Order not found or cannot cancel")

    await db.execute(
        update(Order).where(Order.id == order_id).values(status=OrderStatus.CANCELLED)
    )
    await db.commit()

    return Ok()
