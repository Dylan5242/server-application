from pydantic import BaseModel, EmailStr, Field
from uuid import uuid4

# 🔹 для регистрации
class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    age: int = Field(gt=0, lt=120)
    is_subscribed: bool


# 🔹 для ответа (без пароля!)
class User(BaseModel):
    id: str
    username: str
    email: EmailStr
    age: int
    is_subscribed: bool


# 🔹 для логина
class LoginData(BaseModel):
    username: str
    password: str