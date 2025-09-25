import unicodedata
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


def _es_palabra_frecuente(token: Token) -> bool:
    """
    Determina si un token corresponde a una palabra frecuente.
    Incluye determinantes, preposiciones, pronombres, conjunciones coordinantes
    y  subordinantes.
    Parámetros:
        token (Token): Token analizado por spaCy.
    Retorna:
        bool: True si el token es considerado palabra frecuente, False en caso contrario.
    """
    # si es determinante
    if token.pos_ == "DET":
        return True
    # si es preposicion
    if token.pos_ == "ADP":
        return True
    # si es pronombre
    if token.pos_ == "PRON":
        return True
    # si es conjuncion coordinante
    if token.pos_ == "CCONJ":
        return True
    # si es conjuncion subordinante
    if token.pos_ == "SCONJ":
        return True
    return False


def _normalizar_token(
        token: Token,
        sin_palabras_frecuentes: bool,
        con_sustantivos_en_singular: bool) -> str | None:
    """
    Normaliza un token según ciertas reglas.
    Reglas aplicadas:
    - Se descartan signos de puntuación (token.is_punct == True).
    - Si 'sin_palabras_frecuentes' es True, se eliminan determinantes, pronombres,
        preposiciones y conjunciones (según _es_palabra_frecuente).
    - Si 'con_sustantivos_en_singular' es True, los sustantivos en plural se
        convierten a su forma singular usando el lemma (token.lemma_.lower()).
    - Los nombres propios (pos_ == "PROPN") se conservan con mayúsculas.
    - El resto de las palabras se devuelven en minúsculas.
    Parámetros:
        token (Token): Token a procesar.
        sin_palabras_frecuentes (bool): Indica si se eliminan palabras frecuentes.
        con_sustantivos_en_singular (bool): Indica si los sustantivos en plural
        deben convertirse a singular.
    Retorna:
        str | None: Palabra normalizada o None si el token fue descartado.

    """
    # ignora signos de puntuacion
    if token.is_punct:
        return None
    # ignora palabras frecuentes
    if sin_palabras_frecuentes and _es_palabra_frecuente(token):
        return None
    # convierte sustantivos plurales a singular
    if con_sustantivos_en_singular:
        if token.pos_ == "NOUN" and "Plur" in token.morph.get("Number"):
            return token.lemma_.lower()
    # conserva nombres propios en mayusculas
    if token.pos_ == "PROPN":
        return token.text
    return token.text.lower()


def _clave_alfabetica_sin_tildes(palabra: str) -> str:
    base = unicodedata.normalize("NFD", palabra)
    sin_tildes = "".join(ch for ch in base if not unicodedata.combining(ch))
    return sin_tildes.lower()

def _contar_palabras_repetidas(palabras: list[str]) -> dict[str, int]:
    """
    Cuenta las repeticiones de palabras de una lista.
    Proceso:
    - Construye un Counter a partir de la lista.
    - Filtra solo aquellas palabras con más de una aparición.
    - Ordena el resultado:
        1. Descendente por cantidad de repeticiones
        2. Alfabéticamente, corrigiendo el orden de palabras acentuadas
           mediante la función _clave_alfabetica_sin_tildes (ej: "árbol" se
           ordena antes de "avion" y no después una palabra con "z").
    Parámetros:
        palabras (list[str]): Lista de palabras normalizadas.
    Retorna:
        dict[str, int]: Diccionario donde cada clave es una palabra repetida
        y el valor es la cantidad de apariciones.
    """
    contador_de_palabras = Counter(palabras)

    resultado = {
        palabra: cantidad_de_apariciones
        for palabra, cantidad_de_apariciones in contador_de_palabras.items()
        if cantidad_de_apariciones > 1
    }

    resultado_ordenado_descendente_por_cantidad_de_repeticiones = {
        palabra: cantidad_apariciones
        for palabra, cantidad_apariciones in sorted(
            resultado.items(), key=lambda item: (-item[1], _clave_alfabetica_sin_tildes(item[0]), item[0])
        )
    }

    return resultado_ordenado_descendente_por_cantidad_de_repeticiones


# Endpoint principal: POST /repeticiones
@app.post("/repeticiones")
def detectar(
    entrada: TextoEntrada,
    sin_palabras_frecuentes: bool = Query(
        False, description="Ignorar artículos, pronombres, preposiciones y conjunciones"
    ),
    con_sustantivos_en_singular: bool = Query(
        False, description="Llevar sustantivos plurales a singular"
    )
):
    """
    Endpoint del servicio de detección de repeticiones de palabras.
    Proceso:
    - Analiza el texto recibido con spaCy.
    - Normaliza los tokens según parámetros recibidos:
        * sin_palabras_frecuentes → descarta artículos, pronombres, etc.
        * con_sustantivos_en_singular → convierte plurales a singular.
    - Retorna un diccionario con las palabras repetidas y sus cantidades.
    Parámetros:
        entrada (TextoEntrada): Objeto con el texto a analizar.
        sin_palabras_frecuentes (bool): Indica si deben descartarse palabras frecuentes.
        con_sustantivos_en_singular (bool): Indica si se deben unificar sustantivos
        plurales en su singular.
    Retorna:
        dict[str, int]: Diccionario con palabras repetidas como clave y número de apariciones
        como valor.
    """
    doc = nlp(entrada.texto)
    tokens = [token for token in doc]

    palabras = [
        palabra
        for token in tokens
        if (palabra := _normalizar_token(token, sin_palabras_frecuentes, con_sustantivos_en_singular))
           is not None
    ]

    return _contar_palabras_repetidas(palabras)
