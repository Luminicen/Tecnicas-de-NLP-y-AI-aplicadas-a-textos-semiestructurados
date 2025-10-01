from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import spacy
from spacy import displacy

app = FastAPI()
nlp = spacy.load("es_core_news_sm")

class TextoEntrada(BaseModel):
    texto: str
    

def valor(doc):
    for token in doc:
        if token.pos_ in {"VERB", "ADJ","NOUN"} and (negEncontrada(token.lemma_.lower()) + bucleHerencia(token,negEncontrada(token.lemma_.lower())) >= 2):
            return True
    return False


def negEncontrada(palabra):    
    negativo = {
    "nadie", "falso", "ninguno","ningun", "negar",
    "no", "nunca", "jamás", "ni", "apenas", "tampoco",
    "ausencia", "falta", "carencia", "deficiencia",
    "imposible", "incapaz", "inviable", "inválido", "equivocado", "insuficiente",
    "carecer", "desaprobar", "fallar", "rechazar", "omitir",
    "insatisfactorio", "incorrecto", "ineficaz", "incompleto","mentira"
    }
    return 1 if palabra in negativo else 0


def bucleHerencia(padre,valorInicial,contadorN=0):   
    penalizar=-100 
    for hijo in (h for h in padre.children if h.dep_ in ["ccomp", "xcomp", "acl","csubj","advmod","nsubj","mark","obj"]):
        #Verificamos si es un caso de refuerzo negativo.
        if (hijo.pos_=="SCONJ" and padre.pos_!="VERB") or hijo.dep_=="obj":                        
            return penalizar;
        contadorN+=negEncontrada(hijo.lemma_.lower())
        if contadorN>=2-valorInicial: #si el primer token es negativo necesito 1 sino se necesitan 2:
            return contadorN
        #Avanzamos por los hijos que nos permiten seguir buscando negaciones.
        if hijo.dep_ in ["ccomp","xcomp", "acl","csubj","nsubj"]:
            contadorN+=bucleHerencia(hijo,valorInicial)
            if contadorN>=2-valorInicial: #si el primer token es negativo necesito 1 sino se necesitan 2:
                return contadorN
            if contadorN <0:
                return penalizar
    return contadorN

# Endpoint principal
@app.post("/negativaCompleja")
def convertir_texto(entrada: TextoEntrada):
    return {valor(nlp(entrada.texto))}

# Endpoint de prueba
@app.get("/")
def root():
    return {"mensaje": "API de detección de negativa compleja. Usa POST /negativaCompleja"}

# Nuevo endpoint para visualización
@app.get("/visualizar", response_class=HTMLResponse)
def visualizar(texto: str):
    doc = nlp(texto)
    html = displacy.render(doc, style="dep", page=True)
    return HTMLResponse(content=html)