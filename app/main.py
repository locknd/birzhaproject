from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.api.public  import router as public_router
from app.api.balance import router as balance_router
from app.api.orders  import router as orders_router

app = FastAPI(
    title="Test",
    version="0.1.0",
    description="Мини-биржа"
)

# Подключаем роуты
app.include_router(auth_router)
app.include_router(public_router)
app.include_router(balance_router)
app.include_router(orders_router)


# Опционально: простой healthcheck
@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}