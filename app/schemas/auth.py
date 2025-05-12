from pydantic import BaseModel, Field
from uuid import UUID
from enum import Enum

class UserRole(str, Enum):
    USER  = "USER"
    ADMIN = "ADMIN"

class NewUser(BaseModel):
    name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Уникальное имя пользователя",
    )
    
    class Config:
        schema_extra = {
            "example": {"name": "ivan_ivanov"}
        }

class UserOut(BaseModel):
    id:      UUID     = Field(..., description="UUID пользователя")
    name:    str      = Field(..., description="Имя пользователя")
    role:    UserRole = Field(..., description="Роль пользователя")
    api_key: str      = Field(..., description="API-ключ для запросов")

    class Config:
        schema_extra = {
            "example": {
                "id":      "35b0884d-9a1d-47b0-91c7-eecf0ca56bc8",
                "name":    "ivan_ivanov",
                "role":    "USER",
                "api_key": "key-550e8400-e29b-41d4-a716-446655440000"
            }
        }