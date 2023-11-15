from sqlalchemy import Boolean, Column, DateTime, ForeignKey, ForeignKeyConstraint, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .engine import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    notification_count = Column(Integer, default=0)
    videos = relationship("Video", back_populates="owner")


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(255), unique=True)
    title = Column(String(255), index=True)
    status = Column(String(255))
    description = Column(String(255), index=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    owner_uuid = Column(String(255), ForeignKey("users.username"))
    view_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    owner = relationship("User", back_populates="videos")



class Like(Base):
    __tablename__ = "likes"

    user_uuid =  Column(String(255), ForeignKey("users.username"), primary_key=True)
    video_uuid = Column(String(255), ForeignKey("videos.uuid"), primary_key=True)


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id =  Column(Integer, ForeignKey("users.id"), primary_key=True, index=True)
    username =  Column(Integer, ForeignKey("users.username"), primary_key=True, index=True)
    video_uuid = Column(String(255), ForeignKey("videos.uuid"), primary_key=True, index=True)
    content = Column(String(255))
    day = Column(DateTime)
   

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id =  Column(Integer, ForeignKey("users.id"))
    type = Column(String(255))
    video_uuid = Column(String(255), ForeignKey("videos.uuid"))
    read = Column(Boolean, default=False)
    day = Column(DateTime)
