import json, os

from typing import Annotated
from dotenv import load_dotenv

from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, Response, HTTPException, status
from app.models.token_model import TokenData

from app.handlers.presigned_url_handler import get_m3u8_master_from_s3, get_m3u8_presigned_from_s3
from app.rabbitmq.engine import rabbitmq
from app.utils.auth import OAuth2PasswordBearerWithCookie
from app.db.engine import SessionLocal
from app.db import crud
from app.sio.socket_io import sio

from jose import JWTError, jwt




load_dotenv()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(prefix="/api/m3u8")

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/get-presigned-url")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

@router.get("/request_presigned/{path}/{filename}")
async def get_legacy_data(path: str, filename: str,
                           token: Annotated[str, Depends(oauth2_scheme)],
                           db: Session = Depends(get_db)):
    
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
    user_name = crud.get_user_by_username(db, username=token_data.username).username


    content_type, content = get_m3u8_presigned_from_s3(path, filename)
    video_owner = crud.get_user_by_video(db=db, video_name=path).username
    new_views = crud.change_video_view(db, path, 0)

    if (user_name != video_owner):
        new_views = crud.change_video_view(db, path, 1)
    # await sio.emit(path, new_views)
    rabbitmq.send_data_exchange(exchange_name='socketio', data=json.dumps({"socket_name":path, "data":new_views}))

    return Response(content, media_type=content_type)


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/whoami")   #changed to use our implementation

@router.get("/static/{path}/{filename}")
async def get_site(path, filename, token: Annotated[str, Depends(oauth2_scheme)],):

    content_type, content = get_m3u8_master_from_s3(path, filename, router)

    return Response(content, media_type=content_type)
