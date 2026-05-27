from decimal import Decimal

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    price: Decimal = Field(gt=0, decimal_places=2)
    count: int = Field(ge=0)
    description: str = Field(min_length=1, max_length=500)


class ProductOut(ProductCreate):
    id: int

    model_config = {"from_attributes": True}
