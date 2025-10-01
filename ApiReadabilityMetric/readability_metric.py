import spacy
import pyphen
from fastapi import FastAPI
import sys

nlp = spacy.load("es_core_news_sm")
dic = pyphen.Pyphen(lang='es')
app = FastAPI()

max_float = sys.float_info.max
min_float = -sys.float_info.max
NIVELES_LEGIBILIDAD = {
    "Muy Fácil": (90, max_float),
    "Fácil": (80, 89),
    "Algo facíl": (70, 79),
    "Normal (para adulto)": (60, 69),
    "Algo dificil": (50, 59),
    "Dificil": (30, 49),
    "Muy dificil": (min_float, 29)
}

def obtener_nivel_legibilidad(valor):
    """
    Recibe un valor numérico y el nombre de la métrica, devuelve el string del nivel correspondiente.
    """
    for nivel, (minimo, maximo) in NIVELES_LEGIBILIDAD.items():
        if minimo <= valor <= maximo:
            return nivel
    return "Nivel desconocido"

def contar_silabas(texto):
    palabras = texto.split()
    total_silabas = sum(len(dic.inserted(palabra).split('-')) for palabra in palabras)
    print("Cantidad de sílabas:", total_silabas)
    return total_silabas

def fernandez_huerta(text):
    """
    Formula de Fernandez Huerta:
    L = 206.84 - 0.60 * (silabas / palabras) - 1.02 * (palabras / oraciones)
    """
    cant_palabras = len(text.split())
    cant_silabas = contar_silabas(text)
    cant_oraciones = text.count('.') + text.count('!') + text.count('?')
    silabas_cada_100_palabras = (cant_silabas / cant_palabras) * 100
    if cant_oraciones == 0:
        cant_oraciones = 1
    palabras_por_oracion = cant_palabras / cant_oraciones
    
    resultado = 206.84 - 0.6 * silabas_cada_100_palabras - 1.02 * palabras_por_oracion
    return resultado

@app.get("/metrica-legibilidad/")
def calcular_legibilidad(texto: str):
    fernandez_huerta_score = fernandez_huerta(texto)
    nivel = obtener_nivel_legibilidad(fernandez_huerta_score)
    return {
        "Puntaje": fernandez_huerta_score,
        "Nivel de legibilidad": nivel
    }