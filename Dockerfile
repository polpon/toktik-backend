# Use an official Python runtime as a parent image
FROM python:3.12-slim

RUN apt update && pip install poetry

WORKDIR /app
COPY . /app

RUN poetry install

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]