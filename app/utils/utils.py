from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.models.tokenModel import TokenData

from app.db.engine import SessionLocal, engine
from app.db import models

from app.models.userModel import UserInDB
from app.utils.auth import OAuth2PasswordBearerWithCookie

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "a87fa0c0149a26f02696619942c15a588794b8abe1fdb9ff55b6aac08ec4b0c7"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



# async def get_current_active_user(
#     current_user: Annotated[User, Depends(get_current_user)]
# ):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user