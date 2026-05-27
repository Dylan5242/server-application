from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Product
from schemas import ProductCreate, ProductOut


app = FastAPI(title="KR-4 Task 9.1")


@app.get("/")
async def root():
    return {"message": "Run Alembic migrations before using product endpoints"}


@app.post("/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: Annotated[Session, Depends(get_db)],
):
    product = Product(**product_data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@app.get("/products", response_model=list[ProductOut])
async def list_products(db: Annotated[Session, Depends(get_db)]):
    return db.query(Product).order_by(Product.id).all()


@app.get("/products/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, db: Annotated[Session, Depends(get_db)]):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
