from fastapi import FastAPI
from models import User, UserAge, Feedback

user = User(name "Лавров Максим Огузович", id=1)

application = FastAPI()

@application.get("/")
async def root():
    return {"message": "Добро пожаловать в моё приложение FastAPI!"}

@application.get("/users")
async def get_user():
    return user

@application.post("/user")
async def check_user(user_data: UserAge):
    return {
        "name": user_data.name,
        "age": user_data.age,
        "is_adult": user_data.age >= 18
    }

feedbacks = []

@application.post("/feedback")
async def create_feedback(fb: Feedback):
    feedbacks.append(fb.dict())
    return {"message": f"Спасибо, {fb.name}! Ваш отзыв сохранён."}
