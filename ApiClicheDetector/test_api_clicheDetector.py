import pytest
from fastapi.testclient import TestClient
from api_clicheDetector import app 
from fastapi import FastAPI

client = TestClient(app)

def test_sin_cliches():
    response = client.post("/detectar_cliches/", json={"texto": "Este texto es completamente original."})
    assert response.status_code == 200
    assert response.json() == {"cliches_encontrados": []}


def test_con_cliche():
    response = client.post("/detectar_cliches/", json={"texto": "Quiero un sistema fácil de usar."})
    assert response.status_code == 200
    encontrados = [c.lower() for c in response.json()["cliches_encontrados"]]
    assert "un sistema fácil de usar" in encontrados

def test_varios_cliches():
    texto = "Quiero que sea seguro y quiero que nunca falle."
    response = client.post("/detectar_cliches/", json={"texto": texto})
    assert response.status_code == 200
    encontrados = [c.lower() for c in response.json()["cliches_encontrados"]]
    assert "que sea seguro" in encontrados
    assert "que nunca falle" in encontrados


def test_variacion_simplicidad():
    texto = "Me gustaría tener más simplicidad en el sistema."
    response = client.post("/detectar_cliches/", json={"texto": texto})
    assert response.status_code == 200
    encontrados = [c.lower() for c in response.json()["cliches_encontrados"]]
    assert "quiero simplicidad" in encontrados

def test_variacion_moderno():
    texto = "Espero que el sistema luzca moderno y esté actualizado."
    response = client.post("/detectar_cliches/", json={"texto": texto})
    assert response.status_code == 200
    encontrados = [c.lower() for c in response.json()["cliches_encontrados"]]
    assert "que sea moderno y actual" in encontrados