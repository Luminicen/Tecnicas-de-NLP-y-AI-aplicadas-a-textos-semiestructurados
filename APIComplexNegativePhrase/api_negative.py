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
        if token.pos_ in {"VERB", "ADJ","NOUN"}:
            estado = {'neg_SCONJ_csubj': False, 'neg_nsubj': False, 'neg_obj': False, "ref_nadie": False}
            total = negEncontrada(token.lemma_.lower()) + bucleHerencia(token, negEncontrada(token.lemma_.lower()), estado)
            if total >= 2:  # doble negación
                return True
    return False


def negEncontrada(palabra):    
    negativo = {
    "apenas","ausencia","abstener","abstenerse","carecer","carencia","desaprobar","deficiencia", "dudar","duda",
    "equivocado","falso","fallar","falta","improbable","imposible",
    "incapaz","incompleto","ineficaz","inviable","incorrecto","insatisfactorio",
    "insuficiente","inconcebible ","mentira","negar","nadie","ninguno","ningun",
    "no","nunca","jamás","ni","renegar","rechazar", "rechazo","sin","tampoco"
    
}       
    return 1 if palabra in negativo else 0


def bucleHerencia(padre,valorInicial,estado,contadorN=0):   
    penalizar=-100 
    for hijo in (h for h in padre.children if h.dep_ in ["ccomp", "xcomp", "acl","csubj","advmod","nsubj","mark","obj","det","advcl"]):
        #Verificamos si es un caso de refuerzo negativo.
        if hijo.dep_ in ["advcl","advmod"]:#posible refuerzo con una sola negacion
            estado["ref_nadie"]= True
        if hijo.dep_ == "mark" and hijo.pos_ == "SCONJ":
            # Evaluamos la subordinada, para esto analisamos si la sub oracion a la que pertenece es usada como sujeto de la oracion principal o como complemento
            if hijo.head.dep_ in ["csubj"]: # seguir ritmo normal si es ccomp o xcomp
                # Posible reforzada
                estado["neg_SCONJ_csubj"] = True
        # Marcar negaciones en nsubj y obj para evitar falsos positivos de refuerzo cuando son doble negación
        if hijo.dep_ == "nsubj":
            if hijo.lemma_.lower() == "nadie" and estado["ref_nadie"]:
                return penalizar
            estado["neg_nsubj"] = estado["neg_nsubj"] or bool(negEncontrada(hijo.lemma_.lower()))
        if hijo.dep_ == "obj" and hijo.lemma_.lower() in ["nada","nadie"]:
            estado["neg_obj"] = estado["neg_obj"] or bool(negEncontrada(hijo.lemma_.lower()))
        
        contadorN+=negEncontrada(hijo.lemma_.lower())
        if contadorN>=2-valorInicial: #si el primer token es negativo necesito 1 sino se necesitan 2:
            return penalizar if estado["neg_SCONJ_csubj"] or (estado["neg_obj"]) else contadorN
        #Avanzamos por los hijos que nos permiten seguir buscando negaciones.
        if hijo.dep_ in ["ccomp","xcomp", "acl","csubj","nsubj"]:
            contadorN+=bucleHerencia(hijo,valorInicial,estado)
            if contadorN>=2-valorInicial: 
                return penalizar if estado["neg_SCONJ_csubj"] or (estado["neg_obj"]) else contadorN
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