import json

from typing import Annotated
from dotenv import load_dotenv

from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, Response

from app.handlers.presigned_url_handler import get_m3u8_master_from_s3, get_m3u8_presigned_from_s3
from app.rabbitmq.engine import rabbitmq
from app.utils.auth import OAuth2PasswordBearerWithCookie
from app.db.engine import SessionLocal
from app.db import crud
from app.sio.socket_io import sio

load_dotenv()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(prefix="/api/m3u8")


@router.get("/request_presigned/{path}/{filename}")
async def get_legacy_data(path: str, filename: str, db: Session = Depends(get_db)):

    content_type, content = get_m3u8_presigned_from_s3(path, filename)

    new_views = crud.change_video_view(db, path, 1)
    # await sio.emit(path, new_views)
    rabbitmq.send_data_exchange(exchange_name='socketio', data=json.dumps({"socket_name":path, "data":new_views}))

    return Response(content, media_type=content_type)


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/whoami")   #changed to use our implementation

@router.get("/static/{path}/{filename}")
async def get_site(path, filename, token: Annotated[str, Depends(oauth2_scheme)],):

    content_type, content = get_m3u8_master_from_s3(path, filename, router)

    return Response(content, media_type=content_type)
