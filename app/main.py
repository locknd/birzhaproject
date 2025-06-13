from fastapi import FastAPI
from app.api.public  import router as public_router
from app.api.balance import router as balance_router
from app.api.orders  import router as orders_router
from app.api.admin  import router as admins_router
from app.api.user import router as user_router

app = FastAPI(
    title="Test",
    version="0.1.0",
    description="Мини-биржа"
)


# Подключаем роуты
app.include_router(public_router)
app.include_router(balance_router)
app.include_router(orders_router)
app.include_router(admins_router)
app.include_router(user_router)