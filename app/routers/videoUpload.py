from fastapi import APIRouter, Depends

from app.handlers.presignedUrlHandler import get_presigned_url_upload
from app.models.fileModel import File, RandomFileName
import pika


router = APIRouter()

@router.post("/get-presigned-url")
async def getPresignedUrl(file: File):
    return get_presigned_url_upload(file.filename, file.filetype)


@router.post("/upload-completed")
async def uploadComplete(randomFN: RandomFileName):
    print(randomFN.filename)

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='from.backend')

    channel.basic_publish(exchange='',
                        routing_key='from.backend',
                        body=randomFN.filename)
    print(f" [x] Sent '{randomFN.filename}'")
    connection.close()
    return


@router.post("/process-completed")
async def processComplete(randomFN: RandomFileName):
    print("processing completed for: "+randomFN.filename)
    return