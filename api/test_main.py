import pytest
from fastapi.testclient import TestClient
from main import api  

client = TestClient(api)

def test_get_index():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {"Validité": "OK"}

def test_nb_restaurants():
    response = client.get('/nb_restaurants')
    assert response.status_code == 200
    assert "Nb Restaurants chargés " in response.json()

def test_nb_avis():
    response = client.get('/nb_avis')
    assert response.status_code == 200
    assert "Nb Avis chargés " in response.json()

def test_liste_restaurants():
    response = client.get('/liste_restaurants')
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Vérifie que la réponse est une liste

def test_liste_avis():
    response = client.get('/liste_avis')
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Vérifie que la réponse est une liste

def test_nb_avis_by_resto():
    response = client.get('/nb_avis/1')
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Vérifie que la réponse est une liste

def test_get_avis_by_resto():
    response = client.get('/avis/1')
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Vérifie que la réponse est une liste

def test_get_restaurant_classement():
    response = client.get('/restaurant_classement/1')
    assert response.status_code == 200
    data = response.json()
    assert "id_resto" in data
    assert "nom" in data
    assert "score" in data
    assert "classement" in data

def test_get_avis_stats():
    response = client.get('/avis_stats/1')
    assert response.status_code == 200
    data = response.json()
    assert "nb_note" in data
    assert "moyenne" in data
    assert "mediane" in data

def test_top_10_restaurants():
    response = client.get('/top_10_restaurants')
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Vérifie que la réponse est une liste
    assert len(response.json()) <= 10  # Vérifie que la liste contient au plus 10 éléments

