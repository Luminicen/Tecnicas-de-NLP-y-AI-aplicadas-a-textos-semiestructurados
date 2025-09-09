from fastapi import FastAPI
from pydantic import BaseModel
from collections import Counter

app = FastAPI(title="Detección de repetición de palabras", version="1.0")


class TextoEntrada(BaseModel):
    texto: str


def contar_palabras_repetidas(texto: str) -> dict[str, str]:
    contador_de_palabras = Counter(texto.lower().split())

    resultado = {
        palabra: cantidad_de_apariciones
        for palabra, cantidad_de_apariciones in contador_de_palabras.items()
        if cantidad_de_apariciones > 1
    }

    resultado_ordenado_descendente_por_cantidad_de_repeticiones = {
        palabra: cantidad_apariciones
        for palabra, cantidad_apariciones in sorted(
            resultado.items(), key=lambda item: item[1], reverse=True)
    }

    return resultado_ordenado_descendente_por_cantidad_de_repeticiones


# Endpoint principal: POST /repeticiones
@app.post("/repeticiones")
def detectar(entrada: TextoEntrada):
    return contar_palabras_repetidas(entrada.texto)

# Endpoint de prueba
@app.get("/")
def root():
    return {"mensaje": "API Detector de repeticiones de palabras. Usa POST /repeticiones con JSON { 'texto': '...' }"}