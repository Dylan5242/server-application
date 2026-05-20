import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from pydantic import BaseModel

load_dotenv(Path(__file__).with_name(".env"))

MODE = os.getenv("MODE", "DEV").upper()
DOCS_USER = os.getenv("DOCS_USER", "")
DOCS_PASSWORD = os.getenv("DOCS_PASSWORD", "")

if MODE not in {"DEV", "PROD"}:
    raise RuntimeError("Invalid MODE value. Use DEV or PROD.")

if MODE == "DEV" and (not DOCS_USER or not DOCS_PASSWORD):
    raise RuntimeError("DOCS_USER and DOCS_PASSWORD must be set in DEV mode.")

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
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


def auth_docs(credentials: HTTPBasicCredentials = Depends(security)) -> None:
    username_is_correct = secrets.compare_digest(credentials.username, DOCS_USER)
    password_is_correct = secrets.compare_digest(credentials.password, DOCS_PASSWORD)

    if not (username_is_correct and password_is_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect docs username or password",
            headers={"WWW-Authenticate": "Basic"},
        )


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


if MODE == "DEV":

    @app.get("/openapi.json", include_in_schema=False, dependencies=[Depends(auth_docs)])
    async def openapi_json():
        return JSONResponse(app.openapi())

    @app.get("/docs", include_in_schema=False, dependencies=[Depends(auth_docs)])
    async def docs():
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title="FastAPI DEV docs",
        )
