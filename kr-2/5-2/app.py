from fastapi import FastAPI, Request, Response, HTTPException
from itsdangerous import Signer, BadSignature
from uuid import uuid4

# Импортируем модели
from models import LoginData, User

app = FastAPI()

# Секретный ключ (в реальном проекте берите из .env)
SECRET_KEY = "your-very-secret-key-12345"
signer = Signer(SECRET_KEY)

# Имитация БД. Ключи — username, значения — данные пользователя
users_db = {
    "alice": {
        "id": "550e8400-e29b-41d4-a716-446655440000",  # Пример фиксированного UUID
        "username": "alice",
        "password": "secret123",
        "email": "alice@example.com",
        "age": 25,
        "is_subscribed": True
    },
    "bob": {
        "id": str(uuid4()),
        "username": "bob",
        "password": "qwerty",
        "email": "bob@example.com",
        "age": 30,
        "is_subscribed": False
    }
}


# -----------------------------
# 1️⃣ Маршрут /login
# -----------------------------
@app.post("/login")
def login(data: LoginData, response: Response):
    user = users_db.get(data.username)

    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Получаем user_id (UUID)
    user_id = user["id"]

    # Создаем подписанный токен в формате "user_id.signature"
    # itsdangerous.Signer.sign() делает это автоматически
    signed_token = signer.sign(user_id).decode("utf-8")

    # Устанавливаем куку
    response.set_cookie(
        key="session_token",
        value=signed_token,
        httponly=True,
        max_age=3600,  # Кука живет 1 час
        secure=False,  # Для локального теста по HTTP
        samesite="lax"
    )

    return {"message": "Logged in successfully", "debug_token": signed_token}


# -----------------------------
# 2️⃣ Защищённый маршрут /profile
# -----------------------------
@app.get("/profile", response_model=User)
def get_profile(request: Request):
    # 1. Получаем куку
    signed_token = request.cookies.get("session_token")

    if not signed_token:
        raise HTTPException(status_code=401, detail="Unauthorized: No session cookie")

    try:
        # 2. Проверяем подпись и извлекаем user_id
        # Если подпись неверна, вылетит исключение BadSignature
        user_id = signer.unsign(signed_token).decode("utf-8")
    except BadSignature:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid signature")

    # 3. Ищем пользователя по id в нашей "БД"
    user_data = next((u for u in users_db.values() if u["id"] == user_id), None)

    if not user_data:
        raise HTTPException(status_code=401, detail="Unauthorized: User not found")

    return user_data