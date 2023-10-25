from pydantic import BaseModel


class VideoBase(BaseModel):
    title: str | None = "None"
    description: str | None = None
    status: str | None = "uploading"


class VideoCreate(VideoBase):
    uuid: str
    pass


class Video(VideoBase):
    uuid: str
    owner_uuid: str

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    is_active: bool
    videos: list[Video] = []

    class Config:
        orm_mode = True
