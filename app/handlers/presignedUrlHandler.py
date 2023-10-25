import os
from uuid import uuid4
import boto3
import botocore
from dotenv import load_dotenv

load_dotenv()

def get_presigned_url_upload(file_name: str, file_type: str):
        session = boto3.session.Session()
        client = session.client('s3',
                                config=botocore.config.Config(s3={'addressing_style': 'virtual'}), ## Configures to use subdomain/virtual calling format.
                                region_name='sgp1',
                                endpoint_url='https://sgp1.digitaloceanspaces.com',
                                aws_access_key_id=os.getenv('SPACES_KEY'),
                                aws_secret_access_key=os.getenv('SPACES_SECRET'))

        prefix = "buffer/"
        extension = file_name.split(".")[-1]
        filename = str(uuid4())
        key =  prefix + filename + "." + extension
        url = client.generate_presigned_url(ClientMethod='put_object',
                                        Params={'Bucket': 'toktik-s3',
                                                'Key': f'{key}'},
                                        ExpiresIn=300)

        return (url, filename, extension)