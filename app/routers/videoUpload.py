import pika, json, os
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.handlers.presignedUrlHandler import get_presigned_url_upload
from app.models.fileModel import File, RandomFileName
from app.models.tokenModel import TokenData
from app.db.engine import SessionLocal, engine
from app.db import models, schemas, crud

from app.utils.auth import OAuth2PasswordBearerWithCookie

from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


router = APIRouter(prefix="/api")
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/get-presigned-url")

models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/get-presigned-url")
async def getPresignedUrl(
    video: File,
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

    presigned_obj = get_presigned_url_upload(video.uuid, video.filetype)

    crud.create_user_video(db=db, video=schemas.Video(uuid=presigned_obj[1], owner_uuid=token_data.username, title=video.title, description=video.description))
    return {"owner_uuid": token_data.username, "url": presigned_obj[0], "filename": presigned_obj[1], "extension": presigned_obj[2], "title": video.title, "description": video.description}


@router.post("/upload-completed")
async def uploadComplete(
    video: File,
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
        if username != video.owner_uuid:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    crud.change_video_status(db, video.uuid, video.owner_uuid, "processing")

    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', port=5672))
    except:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

    channel = connection.channel()

    channel.queue_declare(queue='from.backend')

    channel.basic_publish(exchange='',
                        routing_key='from.backend',
                        body=json.dumps(video.model_dump()))

    print(f" [x] Sent '{video.uuid}'")
    connection.close()
    return


@router.post("/process-completed")
async def processComplete(
    video: File,
    db: Session = Depends(get_db)
    ):

    crud.change_video_status(db, video.uuid, video.owner_uuid, "ready")

    print("processing completed for: "+ video.filename)
    return