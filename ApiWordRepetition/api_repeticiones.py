from fastapi import FastAPI
from fastapi.params import Query
from pydantic import BaseModel
from collections import Counter
import spacy
from spacy.tokens import Token

nlp = spacy.load("es_core_news_sm")

app = FastAPI(title="Detección de repetición de palabras", version="1.0")


class TextoEntrada(BaseModel):
    texto: str

def eliminar_signos_de_puntuacion(tokens: list[Token]) -> list[Token]:
    return [token for token in tokens if not token.is_punct]

def es_palabra_frecuente(token: Token) -> bool:
    # si es articulo
    if "Art" in token.morph.get("PronType"):
        return True
    # si es preposicion
    if token.pos_ == "ADP":
        return True
    if token.pos_ == "PRON":
        return True
    # si es conjuncion coordinante
    if token.pos_ == "CCONJ":
        return True
    # si es conjuncion subordinante
    if token.pos_ == "SCONJ":
        return True
    return False

def eliminar_palabras_frecuentes(tokens: list[Token]) -> list[Token]:
    return [token for token in tokens if not es_palabra_frecuente(token)]


def filtrar_tokens(tokens: list[Token], sin_palabras_frecuentes: bool) -> list[Token]:
    tokens = eliminar_signos_de_puntuacion(tokens)

    if sin_palabras_frecuentes:
        tokens = eliminar_palabras_frecuentes(tokens)

    return tokens


def contar_palabras_repetidas(palabras: list[str]) -> dict[str, int]:
    contador_de_palabras = Counter(palabras)

    resultado = {
        palabra: cantidad_de_apariciones
        for palabra, cantidad_de_apariciones in contador_de_palabras.items()
        if cantidad_de_apariciones > 1
    }

    resultado_ordenado_descendente_por_cantidad_de_repeticiones = {
        palabra: cantidad_apariciones
        for palabra, cantidad_apariciones in sorted(
            resultado.items(), key=lambda item: item[1], reverse=True
        )
    }

    return resultado_ordenado_descendente_por_cantidad_de_repeticiones


# Endpoint principal: POST /repeticiones
@app.post("/repeticiones")
def detectar(
    entrada: TextoEntrada,
    sin_palabras_frecuentes: bool = Query(
        False, description="Ignorar artículos, pronombres, preposiciones y conjunciones"
    )
):
    doc = nlp(entrada.texto)

    tokens = [token for token in doc]
    tokens = filtrar_tokens(tokens, sin_palabras_frecuentes)
    palabras = [token.text for token in tokens]
    # falta ver mayusculas y palabras a singular

    return contar_palabras_repetidas(palabras)

# Endpoint de prueba
@app.get("/")
def root():
    return {"mensaje": "API Detector de repeticiones de palabras. Usa POST /repeticiones con JSON { 'texto': '...' }"}