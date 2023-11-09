from dotenv import load_dotenv

from ..sio.socket_io import sio

from fastapi import APIRouter

load_dotenv()

router = APIRouter(prefix="/test")

@router.get("/call_view")
async def call_view():
    await sio.emit("hello", "world")
    return "Success"
