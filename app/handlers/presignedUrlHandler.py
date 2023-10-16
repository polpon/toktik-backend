import os
import boto3
import botocore
from dotenv import load_dotenv

load_dotenv()

def get_presigned_url_upload(file_name: str, file_extensin: str):
    session = boto3.session.Session()
    client = session.client('s3',
                            config=botocore.config.Config(s3={'addressing_style': 'virtual'}), ## Configures to use subdomain/virtual calling format.
                            region_name='sgp1',
                            endpoint_url='https://toktik-s3.sgp1.digitaloceanspaces.com',
                            aws_access_key_id=os.getenv('SPACES_KEY'),
                            aws_secret_access_key=os.getenv('SPACES_SECRET'))

    url = client.generate_presigned_url(ClientMethod='put_object',
                                        Params={'Bucket': 'toktik-s3',
                                                'Key': f'{file_name}.{file_extensin}'},
                                        ExpiresIn=300)

    return url