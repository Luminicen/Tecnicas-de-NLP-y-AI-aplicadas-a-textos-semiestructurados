from fastapi import FastAPI,Request
from pydantic import BaseModel
from rapidfuzz import fuzz
import spacy

cliches= [
    "quiero poder",
    "Para poder usar el sistema",
    "para administrar",
    "un sistema fácil de usar",
    "poder hacer clic en un botón",
    "Para mejorar la experiencia del usuario",
    "Para aumentar la productividad",
    "Para que sea más rápido y fácil",
    "Para que funcione mejor",
    "Para que sea más intuitivo",
    "gestionar todo el sistema",
    "guardar datos en la base de datos",
    "refactorizar el código",
    "implementar la API",
    "que sea más bonito",
    "un diseño moderno",
    "que sea seguro",
    "que sea escalable",
    "poder exportar todo",
    "acceder a todo desde cualquier lugar",
    "que nunca falle",
    "que cargue rápido",
    "que sea compatible con todo",
    "que siempre funcione",
    "que nunca falle"
    "que no tenga errores",
    "que la base de datos guarde la información",
    "poder conectarme al servidor",
    "administrar usuarios y permisos",
    "una aplicación que sea la mejor",
    "que sea más eficiente",
    "personalizar todo",
    "una interfaz atractiva",
    "quiero simplicidad",
    "que sea todo más claro",
    "que se integre con cualquier cosa",
    "que sea moderno y actual",
    "que el sistema haga todo automáticamente"
  ]


app = FastAPI()

nlp = spacy.load("es_dep_news_trf")


class TextoEntrada(BaseModel):
    texto: str

@app.post("/detectar_cliches/")
def detectar_cliches_endpoint(entrada: TextoEntrada):
    resultado = detectar_cliches(entrada.texto, cliches, nlp)
    return {"cliches_encontrados": resultado}


def lematizar(texto, nlp):
    doc = nlp(texto.lower())
    return " ".join([token.lemma_ for token in doc if not token.is_punct]   )

def detectar_cliches(texto, lista_cliches, nlp, umbral=70):
    texto_lemmas = lematizar(texto, nlp)
    
    encontrados = []
    for cliche in lista_cliches:
        cliche_lemmas = lematizar(cliche, nlp)
        valor = fuzz.token_set_ratio(cliche_lemmas, texto_lemmas)

        #valor = fuzz.partial_ratio(cliche_lemmas, texto_lemmas)
        
        if valor >= umbral:
            print(f"{cliche} → {valor}") 
            encontrados.append(cliche)
    return encontrados
