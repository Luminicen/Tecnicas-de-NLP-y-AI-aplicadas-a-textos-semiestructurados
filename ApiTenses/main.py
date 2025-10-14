from builtins import str
from fastapi import FastAPI 
import sys

from servicios import invertir_texto, adverbs, detección_de_verbos

app = FastAPI()

@app.get("/invertir_texto/") 
def invertir(texto: str): 
    return invertir_texto.invertir_texto(texto)

@app.get("/adverbs/") 
def detectar_adverbs(texto: str): 
    return adverbs.adverbs(texto)

@app.get("/detección_de_verbos/")
def verificacion(texto: str):
    return detección_de_verbos.detectar_tiempo_verbal(texto)


if len(sys.argv)<1:
    print("Uso: python main.py arg1 ")
    sys.exit(1)


texto = "".join(sys.argv[1:]) 
print(verificacion(texto))