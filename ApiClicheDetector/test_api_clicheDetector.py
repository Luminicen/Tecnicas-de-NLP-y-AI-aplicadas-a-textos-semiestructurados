import pytest
from fastapi.testclient import TestClient
from api_clicheDetector import app 

client = TestClient(app)

def test_sin_cliches():
    response = client.post("/detectar_cliches/", json={"texto": "Este es un texto sin cliches."})
    assert response.status_code == 200
    assert response.json() == {"cliches_encontrados": "No se encontraron cliches"}

def test_con_cliches():
    response = client.post("/detectar_cliches/", json={"texto":"Se encontraron cliches"})
    assert response.status_code == 200
    assert "cliches_encontrados" in response.json()
    assert len(response.json()["cliches_encontrados"]) > 0