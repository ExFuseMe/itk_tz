FROM python:3.12-slim


WORKDIR /app

COPY docker/python/requirements.txt .

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --no-cache-dir --upgrade -r requirements.txt


COPY . .