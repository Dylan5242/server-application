import secrets

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from pydantic import BaseModel

app = FastAPI()
security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
DUMMY_HASH = pwd_context.hash("dummy-password")

fake_users_db: dict[str, "UserInDB"] = {}


class UserBase(BaseModel):
    username: str


class User(UserBase):
    password: str


class UserInDB(UserBase):
    hashed_password: str


def unauthorized_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Basic"},
    )


def auth_user(credentials: HTTPBasicCredentials = Depends(security)) -> UserInDB:
    found_user = None

    for username, user in fake_users_db.items():
        if secrets.compare_digest(credentials.username, username):
            found_user = user

    password_hash = found_user.hashed_password if found_user else DUMMY_HASH
    password_is_correct = pwd_context.verify(credentials.password, password_hash)

    if found_user and password_is_correct:
        return found_user

    raise unauthorized_exception()


@app.post("/register")
async def register(user: User):
    hashed_password = pwd_context.hash(user.password)
    fake_users_db[user.username] = UserInDB(
        username=user.username,
        hashed_password=hashed_password,
    )

    return {"message": f"User {user.username} registered successfully"}


@app.get("/login")
async def login(user: UserInDB = Depends(auth_user)):
    return {"message": f"Welcome, {user.username}!"}
