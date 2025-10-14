from builtins import str
from fastapi import FastAPI 
import sys

import detección_de_verbos

app = FastAPI()

@app.get("/detección_de_verbos/")
def verificacion(texto: str):
    return detección_de_verbos.detectar_tiempo_verbal(texto)
