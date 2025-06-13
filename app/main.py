from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.api.public  import router as public_router
from app.api.balance import router as balance_router
from app.api.orders  import router as orders_router
from app.api.admin   import router as admins_router
from app.api.user    import router as user_router

app = FastAPI(
    title="Test",
    version="0.1.0",
    description="Мини-биржа"
)

# Подключаем роутеры
app.include_router(public_router)
app.include_router(balance_router)
app.include_router(orders_router)
app.include_router(admins_router)
app.include_router(user_router)


# def custom_openapi():
#     if app.openapi_schema:
#         return app.openapi_schema

#     openapi_schema = get_openapi(
#         title=app.title,
#         version=app.version,
#         description=app.description,
#         routes=app.routes,
#     )

#     # 1) Регистрируем SecurityScheme — появится кнопка Authorize
#     openapi_schema["components"]["securitySchemes"] = {
#         "APIKeyHeader": {
#             "type": "apiKey",
#             "in":   "header",
#             "name": "Authorization",
#             "description": "Введите `TOKEN <ваш api_key>`",
#         }
#     }

#     # 2) Для каждого пути — по умолчанию навешиваем security
#     for path, path_item in openapi_schema["paths"].items():
#         # если это public (достаточно посмотреть на префикс)
#         if path.startswith("/api/v1/public"):
#             # убираем замочек
#             for op in path_item.values():
#                 op.pop("security", None)
#         else:
#             # навешиваем нашу схему
#             for op in path_item.values():
#                 op.setdefault("security", [{"APIKeyHeader": []}])

#     app.openapi_schema = openapi_schema
#     return app.openapi_schema

# # Заменяем метод генерации схемы
# app.openapi = custom_openapi