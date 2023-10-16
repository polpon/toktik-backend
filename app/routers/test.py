from fastapi import APIRouter

from app.handlers.presignedUrlHandler import get_presigned_url_upload
from app.models.fileModel import File

router = APIRouter()

@router.post("/test")
async def test(file: File):
    return get_presigned_url_upload(file.filename, file.extension)