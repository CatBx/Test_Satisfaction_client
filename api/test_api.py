from fastapi.testclient import TestClient
from main import api

client = TestClient(api)

def test_get_index():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {'Validité': 'OK'}

def test_get_restaurants():
    response = client.get("/restaurants")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_avis():
    response = client.get("/avis")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_avis_by_resto():
    response = client.get("/avis/1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_count_restaurants():
    response = client.get("/count_restaurants")
    assert response.status_code == 200
    assert "count" in response.json()

def test_count_avis():
    response = client.get("/count_avis")
    assert response.status_code == 200
    assert "count" in response.json()

def test_count_avis_by_resto():
    response = client.get("/avis_count/1")
    assert response.status_code == 200
    assert "count" in response.json()

def test_get_avis_stats():
    response = client.get("/avis_stats/1")
    assert response.status_code == 200
    assert "average" in response.json()
    assert "median" in response.json()

def test_get_restaurants_list():
    response = client.get("/restaurants_list")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

