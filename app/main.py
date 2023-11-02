from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middleware.middleware import MyMiddleware

from .routers import api_auth, api_m3u8, api_video

app = FastAPI()

origins = ["*"]

app.include_router(api_m3u8.router)
app.include_router(api_auth.router)
app.include_router(api_video.router)
app.add_middleware(MyMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)