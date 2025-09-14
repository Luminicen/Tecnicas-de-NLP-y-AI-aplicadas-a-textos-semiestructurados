from fastapi import FastAPI
import spacy
from pydantic import BaseModel

app = FastAPI()
nlp = spacy.load("es_core_news_sm")

class TextoEntrada(BaseModel):
    texto: str
    

def valor(doc):
    for token in doc:
        contadorN=0
        if token.pos_ == "VERB" or token.pos_=="ADJ" :
            contadorN+=negEncontrada(token.lemma_.lower())+bucleHerencia(token,contadorN)
            if contadorN >= 2:
                return True
            return False
    return False

def negEncontrada(palabra):    
    negativo = {
    "nadie", "ninguno","ningun",
    "no", "nunca", "jamás", "ni", "apenas", "tampoco",
    "ausencia", "falta", "carencia", "deficiencia",
    "imposible", "incapaz", "inviable", "inválido", "equivocado", "insuficiente",
    "carecer", "desaprobar", "fallar", "rechazar", "omitir",
    "insatisfactorio", "incorrecto", "ineficaz", "incompleto"
    }
    return 1 if palabra in negativo else 0


def bucleHerencia(padre,contadorN):
    for hijo in (h for h in padre.children if h.dep_ in ["ccomp", "acl","csubj","advmod","nsubj","mark"]):
        if hijo.pos_=="SCONJ" and padre.pos_!="VERB":                        
            return -100;
        contadorN+=negEncontrada(hijo.lemma_.lower())
        if hijo.dep_ in ["ccomp", "acl","csubj","nsubj"]:
            contadorN+=bucleHerencia(hijo,contadorN)
            if contadorN <0:
                return -100
    return contadorN

# Endpoint principal
@app.post("/negativaCompleja")
def convertir_texto(entrada: TextoEntrada):
    return {valor(nlp(entrada.texto))}

# Endpoint de prueba
@app.get("/")
def root():
    return {"mensaje": "API de detección de negativa compleja. Usa POST /negativaCompleja"}