FROM python:3.8-slim

RUN apt-get update -y && apt-get install -y libpq-dev gcc
WORKDIR /app

RUN mkdir -p /app/api_data

COPY ./main.py ./main.py
COPY ./test_api.py ./test_api.py
COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

EXPOSE 8000

CMD uvicorn main:api --host 0.0.0.0 --port 8000
