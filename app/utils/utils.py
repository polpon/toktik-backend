import os
import shutil

from jose import jwt

from fastapi import FastAPI, HTTPException

from datetime import datetime, timedelta

from passlib.context import CryptContext


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def delete_files_in_directory(directory_path):
   try:
     with os.scandir(directory_path) as entries:
       for entry in entries:
         if entry.is_file():
            os.unlink(entry.path)
     print("All files deleted successfully.")
   except OSError:
     print("Error occurred while deleting files.")


def delete_folder_with_contents(folder_path):
    try:
        shutil.rmtree(folder_path)
        print(f"Folder '{folder_path}' and its contents have been deleted successfully.")
    except FileNotFoundError:
        print(f"Folder '{folder_path}' not found.")
    except Exception as e:
        print(f"An error occurred while deleting the folder: {str(e)}")


def verify_format(username: str, password: str):
    if (username == '' or password == ''):
       raise HTTPException(status_code=400, detail="Can't be empty")

    if (len(username) < 6):
        raise HTTPException(status_code=400, detail="Username too short")

    if (len(password) < 8):
        raise HTTPException(status_code=400, detail="Password too short")

    return
