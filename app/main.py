import socketio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middleware.middleware import MyMiddleware

from .routers import api_auth, api_m3u8, api_video, api_test

from .sio import socket_io, ws_no_prefix

app = FastAPI()

origins = ["*"]

socket_io.sio.register_namespace(ws_no_prefix.NoPrefixNamespace("/"))
sio_asgi_app = socketio.ASGIApp(socketio_server=socket_io.sio, other_asgi_app=app)

app.add_route("/socket.io/", route=sio_asgi_app, methods=["GET", "POST"])
app.add_websocket_route("/socket.io/", sio_asgi_app)

app.include_router(api_test.router)
app.include_router(api_m3u8.router)
app.include_router(api_auth.router)
app.include_router(api_video.router)
app.add_middleware(MyMiddleware)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )