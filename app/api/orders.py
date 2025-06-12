from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Union, Dict
from uuid import UUID, uuid4
from datetime import datetime, timezone

from app.deps import get_current_user
from app.schemas import (
    MarketOrderBody, LimitOrderBody,
    MarketOrder, LimitOrder,
    CreateOrderResponse, Ok
)

router = APIRouter(
    prefix="/api/v1/orders",
    tags=["orders"]
)

# In-memory хранилище заявок: order_id -> order
orders: Dict[UUID, Union[MarketOrder, LimitOrder]] = {}

@router.post("/", response_model=CreateOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    body: Union[MarketOrderBody, LimitOrderBody],
    current_user: UUID = Depends(get_current_user)
):
    order_id = uuid4()
    now = datetime.now(timezone.utc)

    if isinstance(body, MarketOrderBody):
        order = MarketOrder(
            id=order_id,
            status="NEW",
            user_id=current_user,
            timestamp=now,
            body=body
        )
    else:
        order = LimitOrder(
            id=order_id,
            status="NEW",
            user_id=current_user,
            timestamp=now,
            body=body,
            filled=0
        )

    orders[order_id] = order
    return CreateOrderResponse(order_id=order_id)

@router.get("/", response_model=List[Union[LimitOrder, MarketOrder]])
async def list_orders(
    current_user: UUID = Depends(get_current_user)
):
    # возвращаем только заявки текущего пользователя
    return [o for o in orders.values() if o.user_id == current_user]

@router.get("/{order_id}", response_model=Union[LimitOrder, MarketOrder])
async def get_order(
    order_id: UUID,
    current_user: UUID = Depends(get_current_user)
):
    order = orders.get(order_id)
    if not order or order.user_id != current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order

@router.delete("/{order_id}", response_model=Ok)
async def cancel_order(
    order_id: UUID,
    current_user: UUID = Depends(get_current_user)
):
    order = orders.get(order_id)
    if not order or order.user_id != current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    del orders[order_id]
    return Ok()