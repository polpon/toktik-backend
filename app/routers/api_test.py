import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from typing import Annotated

from app.models.file_model import RandomFileName

from app.utils.auth import OAuth2PasswordBearerWithCookie
from jose import JWTError, jwt
from app.db.engine import SessionLocal, engine
from ..sio.socket_io import sio
from app.models.token_model import TokenData

from fastapi import APIRouter, Depends, HTTPException, status, Response

from app.db import models, schemas, crud

load_dotenv()




oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/get-presigned-url")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(prefix="/api")

@router.get("/call_view")
async def call_view():
    await sio.emit("hello", "world")
    return "Success"



@router.post("/get_video_view")
async def get_video_view_count(
    file: RandomFileName,
    db: Session = Depends(get_db)
    ):
    view = crud.get_video(db, file.filename).view_count
    await sio.emit(file.filename, view)

    return view



@router.post("/increment-video-view")
async def increment_video_view(
    file: RandomFileName,
    # views: int,
    db: Session = Depends(get_db)
    ):

    new_views = crud.change_video_view(db, file.filename, 1)
    await sio.emit(file.filename, new_views)
    return new_views


@router.post("/get_video_like")
async def get_video_view_count(
    file: RandomFileName,
    db: Session = Depends(get_db)
    ):
    like = crud.get_video(db, file.filename).likes_count
    await sio.emit("getVideoLike" + file.filename, like)

    return like

@router.post("/increment-video-like")
async def increment_video_view(
    file: RandomFileName,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
    ):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    
    user_id = crud.get_user_by_username(db, username=token_data.username).id
    new_likes = crud.add_video_like(db, user_id=user_id, video_name=file.filename)
    await sio.emit("getVideoLike" + file.filename, new_likes)
    print("increment completed for: "+ file.filename + "by 1")
    return new_likes