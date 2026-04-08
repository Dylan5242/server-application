from fastapi import FastAPI, Header, HTTPException, Depends, Response
from pydantic import BaseModel, field_validator
from datetime import datetime
import re

app = FastAPI()


class CommonHeaders(BaseModel):
    user_agent: str
    accept_language: str

    # Валидация Accept-Language (упрощённая)
    @field_validator("accept_language")
    @classmethod
    def validate_accept_language(cls, v: str):
        pattern = r"^[a-zA-Z-]+(,\s*[a-zA-Z-]+(;q=\d\.\d)*)*$"
        if not re.match(pattern, v.replace(" ", "")):
            raise ValueError("Invalid Accept-Language format")
        return v


# Dependency для извлечения заголовков
async def get_common_headers(
    user_agent: str = Header(..., alias="User-Agent"),
    accept_language: str = Header(..., alias="Accept-Language"),
) -> CommonHeaders:
    try:
        return CommonHeaders(
            user_agent=user_agent,
            accept_language=accept_language
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Маршрут /headers
@app.get("/headers")
async def headers(headers: CommonHeaders = Depends(get_common_headers)):
    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language
    }


# Маршрут /info
@app.get("/info")
async def info(
    response: Response,
    headers: CommonHeaders = Depends(get_common_headers)
):
    # Добавляем заголовок с серверным временем
    response.headers["X-Server-Time"] = datetime.utcnow().isoformat()

    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language
        }
    }