import pytest
from fastapi.testclient import TestClient
from api_negative import app 

client = TestClient(app)

def checkeo(ejemplos):
    for texto, esperado in ejemplos:
        response = client.post("/negativaCompleja", json={"texto": texto})
        assert response.status_code == 200
        data = response.json()
        assert data[0] == esperado

def test_negativa_simple():
    ejemplos = [
        # oración, resultado esperado
        ("No se puede lograr.", False),
        ("dudo mucho ese resultado.", False)
    ]

    checkeo(ejemplos)
        
def test_negativa_compleja():
    ejemplos = [
        # oración, resultado esperado
        ("No creo que no venga.", True),
        ("Es imposible que nadie llegue a tiempo.", True),
        ("No es imposible que venga.", True)
    ]

    checkeo(ejemplos)
        
def test_negativa_refuerzo():
    ejemplos = [
        # oración, resultado esperado
        ("Nadie dijo que no fuera dificil", False),
        ("Nunca dijo nada.", False)
    ]
    checkeo(ejemplos)
