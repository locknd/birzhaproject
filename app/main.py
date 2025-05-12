from fastapi import FastAPI
from app.api.auth import router as auth_router

app = FastAPI(
    title="Test",
    version="0.1.0",
    description="Мини-биржа"
)

# Подключаем роуты
app.include_router(auth_router)

# Здесь позже будете include_router(orders_router), admin_router и т.д.

# Опционально: простой healthcheck
@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}