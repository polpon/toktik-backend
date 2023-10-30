import os
import boto3
import botocore

from uuid import uuid4
from dotenv import load_dotenv
from mimetypes import guess_type
from fastapi import Response
from os.path import isfile

from app.utils.utils import delete_folder_with_contents

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


def get_m3u8_presigned_from_s3(path: str, filename: str):
        fullpath = './static/' + path + "/" + filename

        ## Create new buffer folder if it doesnt exist
        if not os.path.exists('static/' + path):
                os.makedirs('static/' + path)

        session = boto3.session.Session()
        client = session.client('s3',
                                config=botocore.config.Config(s3={'addressing_style': 'virtual'}), ## Configures to use subdomain/virtual calling format.
                                region_name='sgp1',
                                endpoint_url='https://sgp1.digitaloceanspaces.com',
                                aws_access_key_id=os.getenv('SPACES_KEY'),
                                aws_secret_access_key=os.getenv('SPACES_SECRET'))

        try:
                client.download_file("toktik-s3-videos", path + "/" + filename, fullpath)
        except:
                return Response(status_code=404)

        if not isfile(fullpath):
                return Response(status_code=404)

        # Read the file content
        with open(fullpath, 'r') as file:
                lines = file.readlines()

        # Iterate through the lines and modify as needed
        with open(fullpath, 'w') as file:
                for line in lines:
                        if line.strip().endswith('.ts'):
                                url = client.generate_presigned_url(ClientMethod='get_object',
                                                        Params={'Bucket': 'toktik-s3-videos',
                                                                'Key': f"{path.strip()}/{line.strip()}"},
                                                        ExpiresIn=80)

                                file.write(url + "\n")
                        else:
                                file.write(line)

        # Put entire file into memory
        with open(fullpath) as f:
                content = f.read()

        delete_folder_with_contents('./static/' + path)

        content_type, _ = guess_type(fullpath)

        return content_type, content


def get_m3u8_master_from_s3(path: str, filename: str, router):
        fullpath = './static/' + path + "/" + filename

        ## Create new buffer folder if it doesnt exist
        if not os.path.exists('./static/' + path):
                os.makedirs('./static/' + path)

        session = boto3.session.Session()
        client = session.client('s3',
                                config=botocore.config.Config(s3={'addressing_style': 'virtual'}), ## Configures to use subdomain/virtual calling format.
                                region_name='sgp1',
                                endpoint_url='https://sgp1.digitaloceanspaces.com',
                                aws_access_key_id=os.getenv('SPACES_KEY'),
                                aws_secret_access_key=os.getenv('SPACES_SECRET'))

        try:
                client.download_file("toktik-s3-videos", path + "/" + filename , fullpath)
        except:
                return Response(status_code=404)

        if not isfile(fullpath):
                return Response(status_code=404)

        # Read the file content
        with open(fullpath, 'r') as file:
                lines = file.readlines()

        # Iterate through the lines and modify as needed
        with open(fullpath, 'w') as file:
                for line in lines:
                        if line.strip().endswith('.m3u8'):
                                # Add "good_" in front of the line
                                new_line = router.prefix + '/request_presigned/' + path + '/' + line
                                file.write(new_line)
                        else:
                                file.write(line)

        # Put the entire file into memory
        with open(fullpath) as f:
                content = f.read()

        delete_folder_with_contents('./static/' + path)

        content_type, _ = guess_type(fullpath)

        return content_type, content