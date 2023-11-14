from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from sqlalchemy.exc import NoResultFound

from . import models, schemas
from datetime import datetime


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

def get_order_video_by_view(db: Session, current_video: int):
    comment = db.query(models.Video).order_by(models.Video.view_count.desc()).offset(current_video).limit(10).all()
    return comment



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

def change_video_view(db: Session, file_name: str, add_views: int):
    try:
        video = db.query(models.Video).filter(models.Video.uuid == file_name).first()
        db.query(models.Video).filter(models.Video.uuid == file_name).update({'view_count': video.view_count + add_views})
        db.commit()
        return db.query(models.Video).filter(models.Video.uuid == file_name).first().view_count
    except Exception as e:
        print(e)
        return 0

def get_video(db: Session, file_name: str):
    return db.query(models.Video).filter(models.Video.uuid == file_name).first()



def check_is_like(db: Session, user_uuid: int, video_name: str):
    return db.query(models.Like).filter_by(user_uuid=user_uuid, video_uuid=video_name).first() is not None

def unlike_video(db: Session, user_uuid: int, video_name: str):
    like = db.query(models.Like).filter_by(user_uuid=user_uuid, video_uuid=video_name).first()
    if like:
        video = db.query(models.Video).filter(models.Video.uuid == video_name).first()
        db.query(models.Video).filter(models.Video.uuid == video_name).update({'likes_count': video.likes_count - 1})
        db.delete(like)
        db.commit()
    return db.query(models.Video).filter(models.Video.uuid == video_name).first().likes_count

def add_video_like(db: Session, user_uuid: int, video_name: str):
    islike = check_is_like(db=db, user_uuid=user_uuid, video_name=video_name)
    if islike is False:
        video = db.query(models.Video).filter(models.Video.uuid == video_name).first()
        db.query(models.Video).filter(models.Video.uuid == video_name).update({'likes_count': video.likes_count + 1})
        db_like = models.Like(user_uuid=user_uuid, video_uuid=video_name)
        db.add(db_like)
        db.commit()
        db.refresh(db_like)
        return db.query(models.Video).filter(models.Video.uuid == video_name).first().likes_count
    else:
        return db.query(models.Video).filter(models.Video.uuid == video_name).first().likes_count


def add_comment(db: Session, user_id: int, video_name: str, comment: str):
    video = db.query(models.Video).filter(models.Video.uuid == video_name).first()
    # user = db.query(models.User).filter(models.User.id == user_id).first()

    todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    db_comment = models.Comment(user_id=user_id, video_uuid=video_name, content=comment, day=todays_datetime)
    if db_comment is not None:
        db.query(models.Video).filter(models.Video.uuid == video_name).update({'comment_count': video.comment_count + 1})
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment

def get_comment_by_id(db: Session, comment_id: int):
    return db.query(models.Comment).filter(models.Comment.id == comment_id).first()

def get_comment_by_id_and_user_id(db: Session, comment_id: int, user_id: int):
    return db.query(models.Comment).filter_by(user_id=user_id, id=comment_id).first()

def get_all_comment_by_video(db: Session, video_name: str):
    comments = db.query(models.Comment).filter(models.Comment.video_uuid == video_name).all()
    return comments

def get_number_of_comment(db: Session, video_name: str):
    num_comments = db.query(models.Comment).filter(models.Comment.video_uuid == video_name).count()
    return num_comments

def get_comment_by_ten(db: Session, video_name: str, start_from: int):
    if start_from == 0:
        comment = db.query(models.Comment).filter(models.Comment.video_uuid == video_name).order_by(models.Comment.id.desc()).limit(10).all()
        return comment
    else:
        comment = db.query(models.Comment).filter(models.Comment.video_uuid == video_name).order_by(models.Comment.id.desc()).filter(models.Comment.id <= start_from).limit(10).all()
        return comment



