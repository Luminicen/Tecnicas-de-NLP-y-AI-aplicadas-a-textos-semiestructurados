import pytest
from fastapi.testclient import TestClient
from ApiUnusualPunctuation.api_punctuation import app

# Creamos un cliente de pruebas para interactuar con la API de forma offline
client = TestClient(app)

def test_root():
    """Verifica que el endpoint raíz '/' esté funcionando."""
    response = client.get("/")
    assert response.status_code == 200
    assert "mensaje" in response.json()

def test_oracion_sin_errores():
    """Prueba una oración correctamente puntuada, que debería devolver una lista vacía."""
    payload = {"sentence": "¡Esta es una oración perfectamente escrita y correcta!"}
    response = client.post("/detectar-puntuacion", json=payload)
    assert response.status_code == 200
    # La respuesta debe ser una lista vacía, ya que no hay errores
    assert response.json() == []

def test_errores_de_capitalizacion():
    """Prueba la detección de errores de mayúsculas/minúsculas."""
    payload = {"sentence": "hola, Y adiós."}
    response = client.post("/detectar-puntuacion", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Debe detectar dos errores
    assert len(data) == 2
    assert data[0]["descripción"] == "La oración debe comenzar con mayúscula"
    assert data[0]["texto"] == "hola"
    assert data[1]["descripción"] == "Uso incorrecto de mayúsculas después de coma"
    assert data[1]["texto"] == ", Y"

def test_puntuacion_excesiva_y_suspensivos():
    """Prueba el uso excesivo de signos y verifica que ignore los puntos suspensivos."""
    payload = {"sentence": "Ayuda!!! Esto es importante..."}
    response = client.post("/detectar-puntuacion", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Solo debe detectar un error (!!!), ignorando los puntos suspensivos (...)
    assert len(data) == 1
    assert data[0]["descripción"] == "Uso excesivo de signos de puntuación"
    assert data[0]["texto"] == "!!!"

def test_errores_de_espaciado():
    """Prueba la detección de espacios incorrectos alrededor de la puntuación."""
    payload = {"sentence": "Esto está mal ,y esto también.Correcto?"}
    response = client.post("/detectar-puntuacion", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Debe detectar 3 errores de espaciado
    assert len(data) == 3
    assert data[0]["descripción"] == "Espacio incorrecto antes de un signo de puntuación"
    assert data[1]["descripción"] == "Falta de espacio después de un signo de puntuación"
    assert data[2]["descripción"] == "Falta de espacio después de un signo de puntuación"

def test_falta_signos_apertura():
    """Prueba la falta de signos de apertura para interrogación y exclamación."""
    payload = {"sentence": "Hola!, Cómo estás?"}
    response = client.post("/detectar-puntuacion", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Debe detectar ambos errores
    assert len(data) == 2
    assert data[0]["descripción"] == "Falta signo de apertura de exclamación (¡)"
    assert data[1]["descripción"] == "Falta signo de apertura de interrogación (¿)"

def test_signos_agrupacion_sin_balancear():
    """Prueba la detección de paréntesis y comillas sin su pareja."""
    payload = {"sentence": "(Esto es un ejemplo 'sin cerrar."}
    response = client.post("/detectar-puntuacion", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Debe detectar dos errores: el ( y la ' que no se cierran
    assert len(data) == 2
    assert data[0]["descripción"] == "Signo de agrupación de apertura sin su pareja de cierre"
    assert data[0]["texto"] == "("
    assert data[1]["descripción"] == "Signo de agrupación de apertura sin su pareja de cierre"
    assert data[1]["texto"] == "'"

def test_oracion_con_multiples_errores():
    """Prueba una oración compleja con varios tipos de errores a la vez."""
    payload = {"sentence": "hola, Qué tal?? (esto es una prueba .adiós"}
    response = client.post("/detectar-puntuacion", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Se esperan 5 errores:
    # 1. "hola" -> no empieza con mayúscula
    # 2. "Qué" -> mayúscula después de coma
    # 3. "??" -> puntuación excesiva
    # 4. "(" -> paréntesis sin cerrar
    # 5. ".adiós" -> falta de espacio
    assert len(data) == 5