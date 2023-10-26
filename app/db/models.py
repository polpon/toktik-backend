from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .engine import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)

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

    owner = relationship("User", back_populates="videos")
