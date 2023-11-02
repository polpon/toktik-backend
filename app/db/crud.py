from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from sqlalchemy.exc import NoResultFound

from . import models, schemas


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_videos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Video).offset(skip).limit(limit).all()


def get_videos_by_user(db: Session, username: str, skip: int = 0):
    return db.query(models.Video).filter(models.Video.owner_uuid == username).offset(skip).all()


def create_user_video(db: Session, video: schemas.Video):
    db_video = models.Video(**video.dict())
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video


def change_video_status(db: Session, video_name: str, username: str, status: str):
    try:
        db.query(models.Video).filter(models.Video.uuid == video_name).filter(models.Video.owner_uuid == username).update({'status': status})
        db.commit()
        return True
    except Exception as e:
        print(e)
        return False


def get_random_video(db: Session, username: str):
    random_videos = db.query(models.Video).filter(models.Video.owner_uuid != username).filter(models.Video.status == 'ready').order_by(func.random()).limit(10).all()
    return random_videos


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def delete_video(db: Session, file_name: str, username: str):

    query = db.query(models.Video).filter(models.Video.uuid == file_name).filter(models.Video.owner_uuid == username)

    if query.exists == 0:
        raise NoResultFound

    db.query(models.Video).filter(models.Video.uuid == file_name).filter(models.Video.owner_uuid == username).delete()
    return