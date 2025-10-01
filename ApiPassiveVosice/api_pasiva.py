from fastapi import FastAPI
from pydantic import BaseModel
import spacy
from fastapi.middleware.cors import CORSMiddleware
# Cargamos el modelo de spaCy
nlp = spacy.load("es_core_news_sm")

# FastAPI app
app = FastAPI(title="Conversor Pasiva a Activa", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Reemplazar * por dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de entrada
class TextoEntrada(BaseModel):
    texto: str

def convertir_pasiva_a_activa(texto: str) -> str:
    doc = nlp(texto)

    for token in doc:
        # 1) Verbo en participio
        if not (token.pos_ == "VERB" and "Part" in token.morph.get("VerbForm")):
            continue

        # 2) Auxiliar hijo (ser/estar en pasado)
        aux = next(
            (c for c in token.children
             if c.dep_ == "aux" and c.lemma_ in {"ser", "estar"}),
            None
        )
        if not aux:
            continue

        # 3) Sujeto paciente (hijo con dep_ nsubj)
        subj = next(
            (c for c in token.children
             if c.dep_ == "nsubj"),
            None
        )
        if not subj:
            continue

        # 4) Complemento agente: "por" es marcador case
        por = next(
            (t for t in doc
             if t.dep_ == "case" and t.lemma_ == "por"),
            None
        )
        if not por:
            continue

        # 5) El head de "por" es el sustantivo agente
        agente_nodo = por.head
        agentes = [t.text for t in agente_nodo.subtree if not (t.dep_ == "case" and t.lemma_ == "por")]
        agente = " ".join(agentes).strip()
        if not agente:
            continue

        # 6) Reconstruimos la activa
        return f"{agente.capitalize()} {token.lemma_} {subj.text.lower()}."

    # Si no hay pasiva explícita
    return texto

# Endpoint principal
@app.post("/convertir")
def convertir_texto(entrada: TextoEntrada):
    activa = convertir_pasiva_a_activa(entrada.texto)
    return {"original": entrada.texto, "activa": activa}

# Endpoint de prueba
@app.get("/")
def root():
    return {"mensaje": "API de conversión de voz pasiva a activa. Usa POST /convertir"}
