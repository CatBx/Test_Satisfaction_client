FROM python:3.8-slim

RUN apt-get update -y && apt-get install -y libpq-dev gcc && apt-get install -y curl
WORKDIR /app

RUN mkdir -p /app/api_data

COPY ./analyse_sentiments.py ./analyse_sentiments.py
COPY ./load_spacy.py ./load_spacy.py
COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt
# Téléchargement du modèle Spacy
RUN python3 load_spacy.py
# Télécharger les corpus TextBlob nécessaires
RUN python -m textblob.download_corpora

CMD python3 analyse_sentiments.py


