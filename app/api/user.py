from fastapi import APIRouter, Depends, HTTPException, status, Request
from uuid import UUID
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_current_user, get_db
from app.models import User, Balance, Order, Transaction
from app.schemas import Ok, UserOut

router = APIRouter(prefix="/api/v1/admin/user", tags=["User"], dependencies=[Depends(get_current_user)])



@router.delete("/{user_id}", response_model=Ok)
async def delete_user(
    request: Request,
    user_id: UUID,
    current_user: User = Depends(get_current_user),  # Получаем объект пользователя
    db: AsyncSession = Depends(get_db),
):
    """
    Удаляет пользователя по его ID. Админ может удалить любого, обычный пользователь — только себя.
    """
    # Проверка на наличие тела в DELETE-запросе
    body = await request.body()
    if body not in (b"", b"{}"):
        raise HTTPException(
            status_code=422,
            detail="DELETE-запрос не должен содержать тело"
        )

    # Проверка прав
    if not (getattr(current_user, "role", None) == "ADMIN" or getattr(current_user, "id", None) == user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account"
        )

    # 1) Удаляем все ордера этого пользователя
    stmt_orders = delete(Order).where(Order.user_id == user_id)
    await db.execute(stmt_orders)

    # 2) Удаляем все балансы этого пользователя
    stmt_balances = delete(Balance).where(Balance.user_id == user_id)
    await db.execute(stmt_balances)

    # 3) Удаляем все транзакции, связанные с этим пользователем
    stmt_transactions = delete(Transaction).where(
        (Transaction.buy_order_id == user_id) | (Transaction.sell_order_id == user_id)
    )
    await db.execute(stmt_transactions)

    # 4) Можно добавить очистку других связанных таблиц (например, жалоб, сообщений, историй и т.д.)
    # stmt_complaints = delete(Complaint).where(Complaint.user_id == user_id)
    # await db.execute(stmt_complaints)

    # 5) Теперь удаляем самого пользователя
    stmt_user = delete(User).where(User.id == user_id)
    res = await db.execute(stmt_user)
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")

    await db.commit()
    return Ok()
