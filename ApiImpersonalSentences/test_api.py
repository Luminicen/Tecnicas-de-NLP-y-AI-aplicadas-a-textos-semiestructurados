import pytest
from fastapi.testclient import TestClient
from api_impersonal import app  # importa tu API

# Creamos cliente de pruebas (PD: Solo prueba la logica de la API offline)
client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    j = response.json()
    assert "mensaje" in j and isinstance(j["mensaje"], str)

@pytest.mark.parametrize("texto", [
    "Se vive bien en esta ciudad.",
    "Llueve desde la madrugada.",
    "Hay muchas opciones disponibles.",
    "Es necesario presentar la documentación.",
    "No se permite fumar en el establecimiento.",
    "Hace frío esta mañana.",
    "Se venden coches usados en ese local."
])
def test_detectar_impersonal_true(texto):
    """Casos que deberían detectarse como impersonales (True)."""
    response = client.post("/detectar", json={"texto": texto})
    assert response.status_code == 200
    data = response.json()
    # estructura básica
    assert "original" in data and "impersonal" in data and "motivo" in data
    # contenido
    assert data["original"] == texto
    assert isinstance(data["impersonal"], bool)
    assert data["impersonal"] is True
    assert isinstance(data["motivo"], str) and data["motivo"].strip() != ""

@pytest.mark.parametrize("texto", [
    "Se comió la manzana.",
    "Juan come manzanas todos los días.",
    "Hace dos años que trabaja aquí.",
    "No creo que no venga.",
    "No vi a nadie"
])
def test_detectar_impersonal_false(texto):
    """Casos que NO deberían detectarse como impersonales (False)."""
    response = client.post("/detectar", json={"texto": texto})
    assert response.status_code == 200
    data = response.json()
    # estructura básica
    assert "original" in data and "impersonal" in data and "motivo" in data
    # contenido
    assert data["original"] == texto
    assert isinstance(data["impersonal"], bool)
    assert data["impersonal"] is False
    assert isinstance(data["motivo"], str) and data["motivo"].strip() != ""
