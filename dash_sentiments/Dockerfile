FROM python:3.8-slim

RUN apt-get update -y && apt-get install -y libpq-dev gcc
WORKDIR /app

RUN mkdir -p /app/api_data

COPY ./dash_analyse_avis.py ./dash_analyse_avis.py
COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

EXPOSE 5001

# Lancement de l'application
CMD python3 dash_analyse_avis.py

