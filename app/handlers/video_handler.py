import os
import boto3
import botocore

from uuid import uuid4
from dotenv import load_dotenv

from app.models.file_model import File

load_dotenv()

bucket_name_main = 'toktik-s3'
bucket_name_videos = 'toktik-s3-videos'


def getrandom(db):
    session = boto3.session.Session()
    client = session.client('s3',
                            config=botocore.config.Config(s3={'addressing_style': 'virtual'}), ## Configures to use subdomain/virtual calling format.
                            region_name='sgp1',
                            endpoint_url='https://sgp1.digitaloceanspaces.com',
                            aws_access_key_id=os.getenv('SPACES_KEY'),
                            aws_secret_access_key=os.getenv('SPACES_SECRET'))

    folder_list = list_folders(client, bucket_name_videos)

    return folder_list


def list_folders(s3_client, bucket_name):
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix='', Delimiter='/', StartAfter=str(uuid4()), MaxKeys=10)
    for content in response.get('CommonPrefixes', []):
        yield content.get('Prefix')


def purge_video_from_tobechunk(video: File):
    session = boto3.session.Session()
    client = session.client('s3',
                            config=botocore.config.Config(s3={'addressing_style': 'virtual'}), ## Configures to use subdomain/virtual calling format.
                            region_name='sgp1',
                            endpoint_url='https://sgp1.digitaloceanspaces.com',
                            aws_access_key_id=os.getenv('SPACES_KEY'),
                            aws_secret_access_key=os.getenv('SPACES_SECRET'))

    try:
        client.delete_object(
            Bucket=bucket_name_main,
            Key='tobechunk/' + video.filename
        )
    except:
        print("Tried to delete from tobechunk but failed")

    try:
        client.delete_object(
            Bucket=bucket_name_videos,
            Key=video.uuid
        )
    except:
        print("Tried to delete from videos but failed")

    print("s3 deletion complete")
    return


def purge_video_from_all(file_name: str):
    session = boto3.session.Session()
    client = session.client('s3',
                            config=botocore.config.Config(s3={'addressing_style': 'virtual'}), ## Configures to use subdomain/virtual calling format.
                            region_name='sgp1',
                            endpoint_url='https://sgp1.digitaloceanspaces.com',
                            aws_access_key_id=os.getenv('SPACES_KEY'),
                            aws_secret_access_key=os.getenv('SPACES_SECRET'))

    response = client.list_objects_v2(Bucket=bucket_name_main, StartAfter='buffer/' + file_name, MaxKeys=1)

    full_name = response.get("NextContinuationToken")

    if (file_name in full_name):
        try:
            client.delete_object(
                Bucket=bucket_name_main,
                Key=full_name
            )
        except:
            print("Tried to delete from buffer but failed")

    try:
        client.delete_object(
            Bucket=bucket_name_main,
            Key='tobechunk/' + file_name + ".mp4"
        )
    except:
        print("Tried to delete from tobechunk but failed")

    try:
        client.delete_object(
            Bucket=bucket_name_videos,
            Key=file_name
        )
    except:
        print("Tried to delete from videos but failed")

    print("s3 deletion complete")
    return