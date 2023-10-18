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

    channel.queue_declare(queue='hello')

    channel.basic_publish(exchange='',
                        routing_key='hello',
                        body=randomFN.filename)
    print(f" [x] Sent '{randomFN.filename}'")
    connection.close()
    return

@router.post("/convert-completed")
async def convertComplete(randomFN: RandomFileName):
    print(randomFN.filename)

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='convert')

    channel.basic_publish(exchange='',
                        routing_key='convert',
                        body=randomFN.filename)
    print(f" [x] Sent '{randomFN.filename}'")
    connection.close()
    return