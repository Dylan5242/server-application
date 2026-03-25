from pydantic import BaseModel, EmailStr, Field
from uuid import uuid4

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: int = Field(gt=0, lt=120)
    is_subscribed: bool


class User(UserCreate):
    id: str = Field(default_factory=lambda: str(uuid4()))

class Product(BaseModel):
    id: int
    name: str
    category: str
    price: float