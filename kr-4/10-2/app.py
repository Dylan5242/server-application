from typing import Any

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field


app = FastAPI(title="KR-4 Task 10.2")


class User(BaseModel):
    username: str = Field(min_length=1)
    age: int = Field(gt=18)
    email: EmailStr
    password: str = Field(min_length=8, max_length=16)
    phone: str | None = "Unknown"


class ValidationErrorResponse(BaseModel):
    message: str
    errors: list[dict[str, Any]]


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": ".".join(str(item) for item in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    response = ValidationErrorResponse(
        message="Request validation failed",
        errors=errors,
    )
    return JSONResponse(status_code=422, content=response.model_dump())


@app.post("/users")
async def create_user(user: User):
    return {
        "message": "User data is valid",
        "user": user.model_dump(),
    }
