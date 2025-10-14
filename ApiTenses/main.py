from builtins import str
from fastapi import FastAPI 
import sys

import detección_de_verbos

app = FastAPI()

@app.get("/detección_de_verbos/")
def verificacion(texto: str):
    return detección_de_verbos.detectar_tiempo_verbal(texto)

if __name__ == "__main__":
if len(sys.argv)<1:
    print("Uso: python main.py arg1 ")
    sys.exit(1)


texto = "".join(sys.argv[1:]) 
print(verificacion(texto))