import os
import boto3
import botocore

from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()

bucket_name = 'toktik-s3'

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


def generaterandom():
    session = boto3.session.Session()
    client = session.client('s3',
                            config=botocore.config.Config(s3={'addressing_style': 'virtual'}), ## Configures to use subdomain/virtual calling format.
                            region_name='sgp1',
                            endpoint_url='https://sgp1.digitaloceanspaces.com',
                            aws_access_key_id=os.getenv('SPACES_KEY'),
                            aws_secret_access_key=os.getenv('SPACES_SECRET'))

        # Create 100 records with a random key
    for i in range(10):
        user = str(uuid4())
        for i in range(10):
            key = str(uuid4())
            client.put_object(Body=f"question={i}".encode(),
                            Bucket=bucket_name,
                            Key=f'videos/{key}')
            client.put_object(Body=f"question={i}".encode(),
                            Bucket=bucket_name,
                            Key=f'users/{user}/{key}')
            print(f"Inserted to {user} with {key}")

    return

def getrandom():
    session = boto3.session.Session()
    client = session.client('s3',
                            config=botocore.config.Config(s3={'addressing_style': 'virtual'}), ## Configures to use subdomain/virtual calling format.
                            region_name='sgp1',
                            endpoint_url='https://sgp1.digitaloceanspaces.com',
                            aws_access_key_id=os.getenv('SPACES_KEY'),
                            aws_secret_access_key=os.getenv('SPACES_SECRET'))
    # Read 3 records and print them
    for i in range(5):
        list_response = client.list_objects_v2(
            Bucket=bucket_name,
            MaxKeys=1,
            Prefix='videos/',
            StartAfter=f'videos/{str(uuid4())}',
        )
        if 'Contents' in list_response:
            key = list_response['Contents'][0]['Key']
            item_response = client.get_object(
                Bucket=bucket_name,
                Key=key
            )
            print({
                'Key': key,
                'Content': item_response['Body'].read().decode('utf-8')
            })
        else:
            print("Didn't find an item. Please try again.")
    return