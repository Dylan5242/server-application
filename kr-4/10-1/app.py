from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel


app = FastAPI(title="KR-4 Task 10.1")


class ErrorResponse(BaseModel):
    error_code: str
    message: str


class ProductNotFoundException(Exception):
    status_code = 404
    error_code = "PRODUCT_NOT_FOUND"

    def __init__(self, product_id: int):
        self.message = f"Product with id={product_id} was not found"


class ProductUnavailableException(Exception):
    status_code = 409
    error_code = "PRODUCT_UNAVAILABLE"

    def __init__(self, product_id: int, requested_count: int):
        self.message = (
            f"Product with id={product_id} cannot be ordered "
            f"in amount {requested_count}"
        )


products = {
    1: {"id": 1, "title": "Notebook", "count": 3},
    2: {"id": 2, "title": "Mouse", "count": 10},
}


@app.exception_handler(ProductNotFoundException)
async def product_not_found_handler(_, exc: ProductNotFoundException):
    print(exc.message)
    error = ErrorResponse(error_code=exc.error_code, message=exc.message)
    return JSONResponse(status_code=exc.status_code, content=error.model_dump())


@app.exception_handler(ProductUnavailableException)
async def product_unavailable_handler(_, exc: ProductUnavailableException):
    print(exc.message)
    error = ErrorResponse(error_code=exc.error_code, message=exc.message)
    return JSONResponse(status_code=exc.status_code, content=error.model_dump())


@app.get("/products/{product_id}")
async def get_product(product_id: int):
    product = products.get(product_id)
    if product is None:
        raise ProductNotFoundException(product_id)
    return product


@app.post("/products/{product_id}/buy")
async def buy_product(product_id: int, count: int = 1):
    product = products.get(product_id)
    if product is None:
        raise ProductNotFoundException(product_id)
    if count <= 0 or count > product["count"]:
        raise ProductUnavailableException(product_id, count)

    product["count"] -= count
    return {"message": "Order created", "product": product}
