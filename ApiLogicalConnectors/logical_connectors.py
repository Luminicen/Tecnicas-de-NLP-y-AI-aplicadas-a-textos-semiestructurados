from fastapi import FastAPI
import spacy
from spacy.matcher import PhraseMatcher

nlp = spacy.load("es_core_news_sm")
app = FastAPI()

def encontrar_conectores_spacy(texto, conectores):
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patrones = [nlp.make_doc(c) for c in conectores]
    matcher.add("CONECTORES", patrones)
    doc = nlp(texto)
    
    resultados = []
    for match_id, start, end in matcher(doc):
        resultados.append(doc[start:end].text)
    return resultados

conectores_comunes = [
    "pero", "sin embargo", "además", "por lo tanto",
    "aunque", "es decir", "en cambio", "así que", "por consiguiente",
    "no obstante", "a pesar de", "de hecho", "por ejemplo",
    "en resumen", "en conclusión", "por otro lado", "mientras que",
    "aun así", "asimismo", "de igual manera", "de la misma forma",
    "en otras palabras", "en efecto", "por ende", "luego", "entonces",
    "así mismo", "de lo contrario", "por supuesto", "en consecuencia", "aun cuando",
    "y", "o"
    ]

@app.get("/conectores-logicos/")
def detectar_conectores(texto: str):
    encontrados = encontrar_conectores_spacy(texto, conectores_comunes)
    return {"conectores": encontrados}