import pika, json
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
SECRET_KEY = "a87fa0c0149a26f02696619942c15a588794b8abe1fdb9ff55b6aac08ec4b0c7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/get-presigned-url")

models.Base.metadata.create_all(bind=engine)


try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', port=5672))
except:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

channel = connection.channel()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/get-presigned-url")
async def getPresignedUrl(
    file: File,
    token: Annotated[str, Depends(oauth2_scheme)],
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

    presigned_obj = get_presigned_url_upload(file.uuid, file.filetype)

    return {"owner_uuid": token_data.username, "url": presigned_obj[0], "filename": presigned_obj[1], "extension": presigned_obj[2]}


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

    crud.create_user_video(db=db, video=schemas.Video(uuid=video.uuid, owner_uuid=video.owner_uuid))

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
    ):
    print("processing completed for: "+ video.filename)
    return