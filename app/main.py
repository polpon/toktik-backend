from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middleware.middleware import MyMiddleware

from .routers import m3u8, getData, auth, videoUpload

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