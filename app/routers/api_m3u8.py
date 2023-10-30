from dotenv import load_dotenv

from fastapi import APIRouter, Response

from app.handlers.presigned_url_handler import get_m3u8_master_from_s3, get_m3u8_presigned_from_s3

load_dotenv()

router = APIRouter(prefix="/api/m3u8")


@router.get("/request_presigned/{path}/{filename}")
async def get_legacy_data(path: str, filename: str):

    content_type, content = get_m3u8_presigned_from_s3(path, filename)

    return Response(content, media_type=content_type)


@router.get("/static/{path}/{filename}")
async def get_site(path, filename):

    content_type, content = get_m3u8_master_from_s3(path, filename, router)

    return Response(content, media_type=content_type)
