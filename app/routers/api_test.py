import os, pika, json
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from typing import Annotated

from app.models.file_model import RandomFileName

from fastapi.encoders import jsonable_encoder
from app.utils.auth import OAuth2PasswordBearerWithCookie
from jose import JWTError, jwt
from app.db.engine import SessionLocal, engine
from ..sio.socket_io import sio
from app.models.token_model import TokenData

from fastapi import APIRouter, Depends, HTTPException, status, Response

from app.db import models, schemas, crud

from app.rabbitmq.engine import rabbitmq

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

router = APIRouter(prefix="/test")

@router.get("/call_view")
async def call_view():
    rabbitmq.send_data_exchange(exchange_name='socketio', data=json.dumps({"socket_name":"4321", "data":"ggwp"}))
    return "Success"


@router.get("/test_socket_server")
async def test_socket_server(
):
    return rabbitmq.send_data_exchange(exchange_name='socketio', data=json.dumps({"socket_name":"1234", "data":"hello world"}))



# @router.post("/get_video_view")
# async def get_video_view_count(
#     file: RandomFileName,
#     db: Session = Depends(get_db)
#     ):
#     view = crud.get_video(db, file.filename).view_count
#     await sio.emit(file.filename, view)

#     return view



# @router.post("/increment-video-view")
# async def increment_video_view(
#     file: RandomFileName,
#     # views: int,
#     db: Session = Depends(get_db)
#     ):

#     new_views = crud.change_video_view(db, file.filename, 1)
#     await sio.emit(file.filename, new_views)
#     return new_views


# @router.post("/get_video_like")
# async def get_video_view_count(
#     file: RandomFileName,
#     db: Session = Depends(get_db)
#     ):
#     like = crud.get_video(db, file.filename).likes_count
#     await sio.emit("getVideoLike" + file.filename, like)

#     return like


# @router.post("/check_like")
# async def check_like(
#     file: RandomFileName,
#     token: Annotated[str, Depends(oauth2_scheme)],
#     db: Session = Depends(get_db)
#     ):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials"
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception

#     print(username, file.filename)

#     is_like = crud.check_is_like(db, username, file.filename)

#     print(is_like)

#     return is_like


# @router.post("/increment-video-like")
# async def increment_video_view(
#     file: RandomFileName,
#     token: Annotated[str, Depends(oauth2_scheme)],
#     db: Session = Depends(get_db)
#     ):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials"
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except JWTError:
#         raise credentials_exception


#     # user_id = crud.get_user_by_username(db, username=token_data.username).id
#     new_likes = crud.add_video_like(db, user_uuid=username, video_name=file.filename)
#     await sio.emit("getVideoLike" + file.filename, new_likes)
#     print("increment completed for: "+ file.filename + "by 1")
#     return new_likes


# @router.post("/unlike-video")
# async def unlike_video(
#     file: RandomFileName,
#     token: Annotated[str, Depends(oauth2_scheme)],
#     db: Session = Depends(get_db)
#     ):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials"
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except JWTError:
#         raise credentials_exception


#     new_likes = crud.unlike_video(db, user_uuid=token_data.username, video_name=file.filename)
#     await sio.emit("getVideoLike" + file.filename, new_likes)
#     return new_likes

# @router.post("/add-comment-video")
# async def create_comment(
#     comment: str,
#     file: RandomFileName,
#     token: Annotated[str, Depends(oauth2_scheme)],
#     db: Session = Depends(get_db)
#     ):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials"
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except JWTError:
#         raise credentials_exception

#     user_id = crud.get_user_by_username(db, username=token_data.username).id

#     new_commnet = crud.add_comment(db=db, user_id=user_id, video_name=file.filename, comment=comment)
#     await sio.emit("getNewComment" + file.filename, jsonable_encoder(new_commnet))
#     print("New comment for: "+ file.filename)
#     print(jsonable_encoder(new_commnet))
#     return new_commnet


# @router.post("/delete-comment")
# async def create_comment(
#     comment_id: int,
#     token: Annotated[str, Depends(oauth2_scheme)],
#     # form_data: OAuth2PasswordRequestForm = Depends(),
#     db: Session = Depends(get_db)
#     ):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials"
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except JWTError:
#         raise credentials_exception
#     user_id = crud.get_user_by_username(db, username=token_data.username).id
#     comment = crud.get_comment_by_id_and_user_id(db=db, comment_id=comment_id, user_id=user_id)

#     if comment is not None:
#         return crud.delete_comment(db=db, comment_id=comment_id)
#     else:
#         raise HTTPException(status_code=401, detail="Unauthorized")

# @router.post("/get-all-comment/{video_name}")
# async def get_all_comment(
#     video_name: str,
#     db: Session = Depends(get_db)
#     ):
#     return crud.get_all_comment_by_video(db=db, video_name=video_name)
