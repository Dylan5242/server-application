import time
from uuid import uuid4
from fastapi import FastAPI, Request, Response, HTTPException
from itsdangerous import Signer, BadSignature

# Импортируем твои модели
from models import LoginData, User

app = FastAPI()

# Настройки безопасности
SECRET_KEY = "your-very-secret-key-12345"
signer = Signer(SECRET_KEY)
SESSION_MAX_AGE = 300  # 5 минут в секундах
RENEWAL_THRESHOLD = 180  # 3 минуты (после которых обновляем куку)

# Имитация БД
users_db = {
    "alice": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
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


# Вспомогательная функция для создания подписанной куки
def create_signed_token(user_id: str):
    current_time = int(time.time())
    # Формат: user_id.timestamp
    payload = f"{user_id}.{current_time}"
    # Метод sign вернет payload.signature
    return signer.sign(payload).decode("utf-8")


# -----------------------------
# 1️⃣ Маршрут /login
# -----------------------------
@app.post("/login")
def login(data: LoginData, response: Response):
    user = users_db.get(data.username)
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_signed_token(user["id"])

    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        max_age=SESSION_MAX_AGE,
        secure=False,
        samesite="lax"
    )
    return {"message": "Logged in successfully"}


# -----------------------------
# 2️⃣ Защищённый маршрут /profile
# -----------------------------
@app.get("/profile", response_model=User)
def get_profile(request: Request, response: Response):
    token = request.cookies.get("session_token")

    if not token:
        raise HTTPException(status_code=401, detail={"message": "Session expired"})

    try:
        # 1. Проверяем подпись и извлекаем данные
        unsigned_data = signer.unsign(token).decode("utf-8")
        # Разбиваем строку назад на ID и время
        user_id, timestamp_str = unsigned_data.split(".")
        last_activity = int(timestamp_str)
    except (BadSignature, ValueError):
        raise HTTPException(status_code=401, detail={"message": "Invalid session"})

    # 2. Проверка времени (5 минут)
    current_time = int(time.time())
    time_passed = current_time - last_activity

    if time_passed >= SESSION_MAX_AGE:
        raise HTTPException(status_code=401, detail={"message": "Session expired"})

    # 3. Логика продления сессии
    # Если прошло >= 3 минут, но < 5 минут — обновляем куку
    if RENEWAL_THRESHOLD <= time_passed < SESSION_MAX_AGE:
        new_token = create_signed_token(user_id)
        response.set_cookie(
            key="session_token",
            value=new_token,
            httponly=True,
            max_age=SESSION_MAX_AGE,
            secure=False,
            samesite="lax"
        )

    # 4. Поиск пользователя
    user_data = next((u for u in users_db.values() if u["id"] == user_id), None)
    if not user_data:
        raise HTTPException(status_code=401, detail={"message": "User not found"})

    return user_data