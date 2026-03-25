from fastapi import FastAPI, Query, HTTPException
from models import User, UserCreate, Product
from typing import List, Optional

app = FastAPI()

products_db = [
    Product(id=1, name="Nothing 2", category="Nothing", price=100),
]

@app.post("/create_user", response_model=User)
def create_user(user: UserCreate):
    return User(**user.model_dump())

@app.get("/product/{product_id}", response_model=Product)
def get_product(product_id: int):
    for product in products_db:
        if product.id == product_id:
            return product

    raise HTTPException(status_code=404, detail="Product not found")

@app.get("/products/search", response_model=List[Product])
def search_products(
    keyword: str,
    category: Optional[str] = None,
    limit: int = Query(default=10, gt=0)
):
    results = []

    for product in products_db:
        if keyword.lower() in product.name.lower():
            if category and product.category != category:
                continue
            results.append(product)

    return results[:limit]