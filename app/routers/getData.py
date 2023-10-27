from fastapi import APIRouter

from app.handlers.presignedUrlHandler import get_presigned_url_upload
from app.models.fileModel import File
import pika
import boto3
import os

router = APIRouter(prefix="/api")

bucket_name_main = "toktik-s3"
bucket_name_videos = "toktik-s3-videos"

@router.get("/get-video-file")
async def getVideoName():
    # session = boto3.session.Session()
    # client = session.client('s3',
    #                     config=botocore.config.Config(s3={'addressing_style': 'virtual'}), ## Configures to use subdomain/virtual calling format.
    #                     region_name='sgp1',
    #                     endpoint_url='https://sgp1.digitaloceanspaces.com',
    #                     aws_access_key_id=os.getenv('SPACES_KEY'),
    #                     aws_secret_access_key=os.getenv('SPACES_SECRET'))

    return {"filename": "1313d9b1-a31c-4ec7-a3c6-0c8e41c11b80"}