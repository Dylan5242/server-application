from fastapi import FastAPI, Request, Response, HTTPException
from uuid import uuid4

# Импортируем созданные вами модели из models.py
from models import LoginData, User, UserCreate

app = FastAPI()

# Имитация БД. Теперь добавим ID, чтобы соответствовать модели User
users_db = {
    "alice": {"id": str(uuid4()), "username": "alice", "password": "secret123", "email": "alice@example.com", "age": 25, "is_subscribed": True},
    "bob": {"id": str(uuid4()), "username": "bob", "password": "qwerty", "email": "bob@example.com", "age": 30, "is_subscribed": False}
}

sessions = {}


@app.post("/login")
def login(data: LoginData, response: Response):
    user = users_db.get(data.username)
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = str(uuid4())
    sessions[token] = data.username

    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=False, # Смените на True в продакшене (HTTPS)
        samesite="lax"
    )

    return {"message": "Logged in successfully"}


# Используем response_model=User, чтобы FastAPI сам убрал пароль и проверил типы данных!
@app.get("/user", response_model=User)
def get_user(request: Request):
    token = request.cookies.get("session_token")
    if not token or token not in sessions:
        raise HTTPException(status_code=401, detail="Unauthorized")

    username = sessions[token]
    user_data = users_db[username]

    return user_data # FastAPI сам превратит этот словарь в модель User (без пароля!)