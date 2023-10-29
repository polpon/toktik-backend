import base64
from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from app.middleware.middleware import MyMiddleware

from app.utils.auth import OAuth2PasswordBearerWithCookie
from fastapi.security.utils import get_authorization_scheme_param
from .routers import m3u8, getData, auth, videoUpload
from fastapi.middleware.cors import CORSMiddleware

from typing import Annotated, Any

from fastapi import Depends, FastAPI, Request, Response

app = FastAPI()

origins = ["*"]

app.include_router(m3u8.router)
app.include_router(auth.router)
app.include_router(videoUpload.router)
app.include_router(getData.router)
app.add_middleware(MyMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)