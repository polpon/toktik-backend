from fastapi import FastAPI
from .routers import test, auth, videoUpload

from typing import Any

from fastapi import Depends, FastAPI, Request, Response

app = FastAPI()

# @app.get("/")
# def root():
#     return {"message": "Hello World"}

app.include_router(test.router)
app.include_router(auth.router)
app.include_router(videoUpload.router)