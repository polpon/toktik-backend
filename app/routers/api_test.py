from dotenv import load_dotenv
from app.db.engine import Session, SessionLocal

from app.models.file_model import RandomFileName

from ..sio.socket_io import sio

from fastapi import APIRouter, Depends

from app.db import models, schemas, crud

load_dotenv()

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
    await sio.emit("hello", "world")
    return "Success"



@router.get("/get_video_view")
async def get_video_view_count(
    file: RandomFileName,
    db: Session = Depends(get_db)
    ):
    view = crud.get_video(db, file.filename).view_count
    await sio.emit("getVideoView" + file.filename, view)

    return



@router.post("/increment-video-view")
async def increment_video_view(
    file: RandomFileName,
    # views: int,
    db: Session = Depends(get_db)
    ):

    new_views = crud.change_video_view(db, file.filename, 1)
    await sio.emit("getVideoView" + file.filename, new_views)
    print("increment completed for: "+ file.filename + "by 1")
    return 


