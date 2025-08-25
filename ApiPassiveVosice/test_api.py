import pytest
from fastapi.testclient import TestClient
from api_pasiva import app  # importa tu API :D

# Creamos cliente de pruebas (PD: Solo prueba la logica de la API offline)
client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "mensaje" in response.json()

def test_convertir_pasiva_simple():
    payload = {"texto": "La carta fue escrita por Juan."}
    response = client.post("/convertir", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["original"] == payload["texto"]
    # comprobamos que el agente esté en la conversión
    assert "Juan" in data["activa"]

def test_convertir_pasiva_plural():
    payload = {"texto": "Los libros fueron leídos por los estudiantes."}
    response = client.post("/convertir", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "estudiantes" in data["activa"]

def test_oracion_activa_no_cambia():
    payload = {"texto": "María come una manzana."}
    response = client.post("/convertir", json=payload)
    assert response.status_code == 200
    data = response.json()
    # No debería cambiar la oración
    assert data["original"] == data["activa"]
def test_convertir_pasiva_maiev():
    payload = {"texto": "Los libros fueron escritos por Maiev."}
    response = client.post("/convertir", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Debe cambiar a voz activa
    assert data["original"] == payload["texto"]
    assert "Maiev" in data["activa"]
    assert "libros" in data["activa"]
    # El verbo debe aparecer en infinitivo ("escribir")
    assert "escribir" in data["activa"]
