import pika, json, sys, os
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.handlers.presigned_url_handler import get_file_from_s3, get_presigned_url_upload
from app.utils.auth import OAuth2PasswordBearerWithCookie
from app.handlers.video_handler import purge_video_from_tobechunk, purge_video_from_all
from app.db.engine import SessionLocal, engine
from app.models.token_model import TokenData
from app.db import models, schemas, crud
from app.models.file_model import File, MessageComment, MessageCommentsStartFrom, RandomFileName
from fastapi.encoders import jsonable_encoder
from ..sio.socket_io import sio

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


    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbit-mq', port=5672))
    except:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        except:
            crud.change_video_status(db, video.uuid, video.owner_uuid, "error")
            return HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Could not connect to Rabbitmq"
                    )

    channel = connection.channel()

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


@router.post("/process-failed")
async def processComplete(
    video: File,
    db: Session = Depends(get_db)
):
    crud.change_video_status(db, video.uuid, video.owner_uuid, "failed")

    purge_video_from_tobechunk(video)

    print("video failed: " + video.filename)
    return

random_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/get_random_video")

@router.post("/get_random_video")
async def get_random_video(
    token: Annotated[str, Depends(random_scheme)],
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
    except JWTError:
        raise credentials_exception

    random_videos = crud.get_random_video(db, username)

    return random_videos


@router.get("/static/{path}/{filename}")
async def get_static_from_s3(path: str, filename: str):

    content_type, content = get_file_from_s3(path, filename)

    return Response(content, media_type=content_type)

delete_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/delete_video")

@router.post("/delete_video")
async def delete_video(
    file: RandomFileName,
    token: Annotated[str, Depends(delete_scheme)],
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
    except JWTError:
        raise credentials_exception

    try:
        crud.delete_video(db, file.filename, username)
        purge_video_from_all(file.filename)
        db.commit()
    except Exception as e:
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unexpected error:, {sys.exc_info()[0]}"
                )

    return

get_user_videos_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/get_user_videos")

@router.get("/get_user_videos")
async def get_user_videos(
    token: Annotated[str, Depends(delete_scheme)],
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
    except JWTError:
        raise credentials_exception

    return crud.get_videos_by_user(db, username)


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


@router.post("/get-video-like")
async def get_video_view_count(
    file: RandomFileName,
    db: Session = Depends(get_db)
    ):
    like = crud.get_video(db, file.filename).likes_count
    await sio.emit("getVideoLike" + file.filename, like)

    return like


@router.post("/check_like")
async def check_like(
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
    except JWTError:
        raise credentials_exception

    print(username, file.filename)

    is_like = crud.check_is_like(db, username, file.filename)

    print(is_like)

    return is_like


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


    # user_id = crud.get_user_by_username(db, username=token_data.username).id
    new_likes = crud.add_video_like(db, user_uuid=username, video_name=file.filename)
    await sio.emit("getVideoLike" + file.filename, new_likes)
    print("increment completed for: "+ file.filename + "by 1")
    return new_likes


@router.post("/unlike-video")
async def unlike_video(
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


    new_likes = crud.unlike_video(db, user_uuid=token_data.username, video_name=file.filename)
    await sio.emit("getVideoLike" + file.filename, new_likes)
    return new_likes

@router.post("/add-comment-video")
async def create_comment(
    comment: MessageComment,
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

    new_commnet = crud.add_comment(db=db, user_id=user_id, video_name=comment.filename, comment=comment)

    await sio.emit("getNewComment" + comment.filename, jsonable_encoder(new_commnet))
    print("New comment for: "+ comment.filename)
    print(jsonable_encoder(new_commnet))
    return new_commnet


@router.post("/get-all-comment/{video_name}")
async def get_all_comment(
    file: RandomFileName,
    db: Session = Depends(get_db)
    ):
    return crud.get_all_comment_by_video(db=db, video_name=file.filename)


@router.post("/get-comment-number/{video_name}")
async def get_comment_number(
    file: RandomFileName,
    db: Session = Depends(get_db)
    ):
    return crud.get_number_of_comment(db=db, video_name=file.filename)



@router.post("/get-comment-number-by-ten/{video_name}")
async def get_comment_by_ten(
    comment: MessageCommentsStartFrom,
    db: Session = Depends(get_db)
    ):
    return crud.get_comment_by_ten(db=db, video_name=comment.filename, start_from=comment.start_from)