from builtins import str
from fastapi import FastAPI 
import sys

import ApiTenses.deteccion_verbos as deteccion_verbos

app = FastAPI()

@app.get("/detección_de_verbos/")
def verificacion(texto: str):
    return deteccion_verbos.detectar_tiempo_verbal(texto)
