FROM python:3.8-slim

RUN apt-get update -y && apt-get install -y libpq-dev gcc

WORKDIR /app

RUN mkdir -p /app/raw_data

COPY ./load_data.py ./load_data.py
COPY ./load_db.sql ./load_db.sql

COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt
