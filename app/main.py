from fastapi import FastAPI
from .routers import test

app = FastAPI()

# @app.get("/")
# def root():
#     return {"message": "Hello World"}

app.include_router(test.router)
