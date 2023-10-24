import base64
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from app.middleware.middleware import MyMiddleware

from app.utils.auth import OAuth2PasswordBearerWithCookie
from fastapi.security.utils import get_authorization_scheme_param
from .routers import test, auth, videoUpload

from typing import Annotated, Any

from fastapi import Depends, FastAPI, Request, Response

app = FastAPI()

app.include_router(test.router)
app.include_router(auth.router)
app.include_router(videoUpload.router)
# app.add_middleware(MyMiddleware)