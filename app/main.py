import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.api.public import router as public_router
from app.api.balance import router as balance_router
from app.api.orders import router as orders_router
from app.api.admin import router as admins_router
from app.api.user import router as user_router

# Настройка логирования ДО создания app
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    level=logging.DEBUG,    
    handlers=[
        logging.StreamHandler(),  # Вывод в консоль
        logging.FileHandler('app.log', mode='a')  # Запись в файл
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Test",
    version="0.1.0",
    description="Мини-биржа"
)

# Middleware для проверки тела в DELETE-запросах
class DeleteBodyValidatorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "DELETE":
            body = await request.body()
            if body not in (b"", b"{}"):
                return JSONResponse(
                    status_code=422,
                    content={"detail": "DELETE-запрос не должен содержать тело"}
                )
        return await call_next(request)

app.add_middleware(DeleteBodyValidatorMiddleware)

# Логируем старт приложения
logger.info("Приложение запущено")

# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request, call_next):
    logger.debug(f"Входящий запрос: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.debug(f"Ответ: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {str(e)}", exc_info=True)
        raise

# Подключаем роутеры
app.include_router(public_router)
app.include_router(balance_router)
app.include_router(orders_router)
app.include_router(admins_router)
app.include_router(user_router)
