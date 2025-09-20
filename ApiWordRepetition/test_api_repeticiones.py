from api_repeticiones import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_detectar_cuando_hay_palabras_repetidas():
    entrada = {
        "texto": "Los animales observan el arbol bajo el sol; el animal mira los arboles bajo el sol."
    }
    response = client.post("/repeticiones", json=entrada)
    assert response.status_code == 200
    assert response.json() == {"los": 2, "el": 2, "sol":2}


def test_detectar_cuando_no_hay_repeticiones_de_palabras():
    entrada = {
        "texto": "No hay lugar como el hogar."
    }
    response = client.post("/repeticiones", json=entrada)
    assert response.status_code == 200
    assert response.json() == {}


def test_detectar_cuando_hay_palabras_repetidas_ignorando_palabras_frecuentes():
    entrada = {
        "texto": "Los animales observan el arbol bajo el sol; el animal mira los arboles bajo el sol."
    }
    response = client.post(
        "/repeticiones",
        json=entrada,
        params={"sin_palabras_frecuentes": True}
    )
    assert response.status_code == 200
    assert response.json() == {"sol":2}


def test_detectar_cuando_hay_palabras_repetidas_con_sustantivos_plurales_convertidos_a_singular():
    entrada = {
        "texto": "Los animales observan el arbol bajo el sol; el animal mira los arboles bajo el sol."
    }
    response = client.post(
        "/repeticiones",
        json=entrada,
        params={"con_sustantivos_en_singular": True}
    )
    assert response.status_code == 200
    assert response.json() == {"animal": 2, "arbol": 2, "sol":2}
