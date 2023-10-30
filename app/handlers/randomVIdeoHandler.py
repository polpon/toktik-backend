import os
import boto3
import botocore

from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()

bucket_name = 'toktik-s3-videos'

def delete():
    session = boto3.session.Session()
    client = session.client('s3',
                            config=botocore.config.Config(s3={'addressing_style': 'virtual'}), ## Configures to use subdomain/virtual calling format.
                            region_name='sgp1',
                            endpoint_url='https://sgp1.digitaloceanspaces.com',
                            aws_access_key_id=os.getenv('SPACES_KEY'),
                            aws_secret_access_key=os.getenv('SPACES_SECRET'))

    all_objects = client.list_objects(Bucket = bucket_name)
    for i in all_objects["Contents"]:
        client.delete_object(Bucket = bucket_name, Key = i["Key"])
        print(f"Deleted {i['Key']}")
    return


def getrandom():
    session = boto3.session.Session()
    client = session.client('s3',
                            config=botocore.config.Config(s3={'addressing_style': 'virtual'}), ## Configures to use subdomain/virtual calling format.
                            region_name='sgp1',
                            endpoint_url='https://sgp1.digitaloceanspaces.com',
                            aws_access_key_id=os.getenv('SPACES_KEY'),
                            aws_secret_access_key=os.getenv('SPACES_SECRET'))

    folder_list = list_folders(client, bucket_name)

    return folder_list


def list_folders(s3_client, bucket_name):
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix='', Delimiter='/', StartAfter=str(uuid4()), MaxKeys=10)
    for content in response.get('CommonPrefixes', []):
        yield content.get('Prefix')