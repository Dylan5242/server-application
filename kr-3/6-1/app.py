from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()
security = HTTPBasic()

CORRECT_USERNAME = "admin"
CORRECT_PASSWORD = "password"


def check_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    if (
        credentials.username != CORRECT_USERNAME
        or credentials.password != CORRECT_PASSWORD
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


@app.get("/login")
async def login(username: str = Depends(check_credentials)):
    return {"message": "You got my secret, welcome"}
