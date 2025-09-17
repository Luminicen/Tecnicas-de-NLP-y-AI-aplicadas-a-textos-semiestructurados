import pytest
from fastapi.testclient import TestClient
from opinion_perception_verbs import app  

client = TestClient(app)

def test_opinion_simple():
    response = client.get("/opinion-percepcion/", params={"texto": "Pienso que este método no es el más adecuado"})
    assert response.status_code == 200
    data = response.json()
    assert "resultado" in data
    lemas = [v["lema"] for v in data["resultado"]]
    assert "pensar" in lemas
    assert any("opinion" in v["tipo"] for v in data["resultado"])

def test_percepcion_multiple():
    response = client.get("/opinion-percepcion/", params={"texto": "María vio la película y escuchó la música"})
    assert response.status_code == 200
    data = response.json()
    lemas = [v["lema"] for v in data["resultado"]]
    assert "ver" in lemas
    assert "escuchar" in lemas
    assert all(v["tipo"] == "percepcion" for v in data["resultado"])

def test_opinion_percepcion_mixta():
    response = client.get("/opinion-percepcion/", params={"texto": "Yo siento un dolor en la espalda"})
    assert response.status_code == 200
    data = response.json()
    v = data["resultado"][0]
    assert v["lema"] == "sentir"
    assert "opinion" in v["tipo"] or "percepcion" in v["tipo"]

def test_sin_verbos_relevantes():
    response = client.get("/opinion-percepcion/", params={"texto": "El auto está estacionado en la calle"})
    assert response.status_code == 200
    data = response.json()
    assert data["resultado"] == []  # No debería detectar nada
