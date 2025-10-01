import spacy
import re
from typing import List, Dict, Any, Tuple

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

try:
    nlp = spacy.load("es_core_news_sm")
except OSError:
    print("Modelo 'es_core_news_sm' no encontrado. Por favor, descárgalo con:\npython -m spacy download es_core_news_sm")
    nlp = None
    
ERROR_DESCRIPTIONS = {
    # Errores de mayúsculas/minúsculas
    "E001": "Uso incorrecto de mayúsculas después de coma",
    "E002": "La oración debe comenzar con mayúscula",
    # Errores de repetición
    "E010": "Uso excesivo de signos de puntuación",
    # Errores de espaciado
    "E020": "Espacio incorrecto antes de un signo de puntuación",
    "E021": "Falta de espacio después de un signo de puntuación",
    # Errores de signos sin pareja
    "E030": "Falta signo de apertura de exclamación (¡)",
    "E031": "Falta signo de apertura de interrogación (¿)",
    "E032": "Signo de agrupación de cierre sin su pareja de apertura",
    "E033": "Signo de agrupación de apertura sin su pareja de cierre",
}

def _create_error_dict(code: str, span: Tuple[int, int], text: str) -> Dict[str, Any]:
    """Crea un diccionario de error estandarizado."""
    return {
        "posición": span,
        "texto": text[span[0]:span[1]],
        "descripción": ERROR_DESCRIPTIONS.get(code, "Error desconocido")
    }

def find_incorrect_capitalization(doc: spacy.tokens.Doc, original_text: str) -> List[Dict]:
    """Detecta mayúsculas incorrectas después de una coma
    y al inicio de una oración.
    """
    errors = []
    # revisa mayúsculas después de una coma
    for token in doc[1:]:
        prev_token = doc[token.i - 1]
        if prev_token.text == "," and token.text[0].isupper() and token.pos_ not in ["PROPN"]:
            start_pos = prev_token.idx
            end_pos = token.idx + len(token.text)
            errors.append(_create_error_dict("E001", (start_pos, end_pos), original_text))
            
    # revisa que cada oración empiece con mayúscula
    for sent in doc.sents:
        # busca el primer caracter que no sea un espacio en blanco
        first_real_token = None
        for token in sent:
            if not token.is_space:
                first_real_token = token
                break
        
        if first_real_token and first_real_token.text[0].islower():
            span = (first_real_token.idx, first_real_token.idx + len(first_real_token.text))
            errors.append(_create_error_dict("E002", span, original_text))
            
    return errors

def find_excessive_punctuation(text: str) -> List[Dict]:
    """Detecta 2 o más signos de puntuación idénticos y seguidos,
    ignorando el caso válido de los puntos suspensivos (...).
    """
    errors = []
    # detecta 2 o más repeticiones de ! ? , .
    pattern = re.compile(r"([!?,.])\1+")
    for match in pattern.finditer(text):
        # se obtiene el texto completo que coincidió con el patrón
        matched_text = match.group(0)        
        # si el texto encontrado es exactamente "...", se ignora y se continúa con la siguiente búsqueda
        if matched_text == '...':
            continue
        errors.append(_create_error_dict("E010", match.span(), text))
    return errors

def find_spacing_errors(text: str) -> List[Dict]:
    """Detecta errores de espaciado alrededor de la puntuación,
    incluyendo paréntesis y comillas.
    """
    errors = []
    # espacio antes de un signo de puntuación de cierre
    pattern_before = re.compile(r"\s+([.,!?;:)\}\]\"'])")
    for match in pattern_before.finditer(text):
        errors.append(_create_error_dict("E020", match.span(1), text))

    # falta de espacio después de un signo de puntuación, seguido de una letra
    pattern_after = re.compile(r"([.,!?;:)\}\]\"'])(?=[a-zA-ZáéíóúÁÉÍÓÚ0-9])")
    for match in pattern_after.finditer(text):
        # excepción para no marcar puntos dentro de números (por ej.: 1.000)
        if match.group(1) == '.' and match.string[match.end()].isdigit():
            continue
        errors.append(_create_error_dict("E021", match.span(1), text))
    return errors

def find_mismatched_punctuation(doc: spacy.tokens.Doc, original_text: str) -> List[Dict]:
    """Detecta la falta de signos de apertura
    para exclamaciones e interrogaciones.
    """
    errors = []
    pattern = re.compile(r'(?:^|,\s*)([^,?!]+[?!])')
    for match in pattern.finditer(original_text):
        clause_text = match.group(1).strip()
        clause_span = match.span(1)
        # para exclamaciones, verifica si falta el signo de apertura
        if clause_text.endswith('!') and not clause_text.startswith('¡'):
            errors.append(_create_error_dict("E030", clause_span, original_text))
        # para interrogaciones, verifica si falta el signo de apertura
        if clause_text.endswith('?') and not clause_text.startswith('¿'):
            errors.append(_create_error_dict("E031", clause_span, original_text))
    return errors

def find_unbalanced_brackets(text: str) -> List[Dict]:
    """Detecta paréntesis, corchetes, llaves y comillas
    que no tienen pareja.
    """
    errors = []
    stack = []
    # se incluyen comillas simples y dobles
    opening_chars = "([{\"'¡¿"
    closing_map = {')': '(', ']': '[', '}': '{', '"': '"', "'": "'"}

    for i, char in enumerate(text):
        if char in opening_chars:
            # manejo especial para comillas: si ya está en la pila, es un cierre
            if char in "\"'":
                if stack and stack[-1][0] == char:
                    stack.pop()
                else:
                    stack.append((char, i))
            else:
                 stack.append((char, i))
        elif char in closing_map:
            if not stack or stack[-1][0] != closing_map[char]:
                errors.append(_create_error_dict("E032", (i, i + 1), text))
            else:
                stack.pop()
    
    # los elementos que queden en la pila son aperturas sin cierre
    for char, i in stack:
        errors.append(_create_error_dict("E033", (i, i + 1), text))
    return errors

def analyze_punctuation(text: str) -> List[Dict[str, Any]]:
    """Función principal que orquesta todas las detecciones."""
    if not nlp:
        raise RuntimeError("El modelo de SpaCy no está cargado.")

    doc = nlp(text)
    all_errors = []

    all_errors.extend(find_incorrect_capitalization(doc, text))
    all_errors.extend(find_excessive_punctuation(text))
    all_errors.extend(find_spacing_errors(text))
    all_errors.extend(find_mismatched_punctuation(doc, text))
    all_errors.extend(find_unbalanced_brackets(text))

    return sorted(all_errors, key=lambda x: x['posición'][0])

app = FastAPI(
    title="Servicio de Detección de Puntuaciones Inusuales",
    description="API para analizar y detectar puntuaciones inusuales en oraciones en español.",
    version="1.1.0" 
)

class SentenceInput(BaseModel):
    sentence: str = Field(..., min_length=1, example="hola, esto es una prueba!! (y creo que va a funcionar.", description="La oración que se desea analizar.")

class PunctuationError(BaseModel):
    posición: tuple[int, int]
    texto: str
    descripción: str

# Endpoint de prueba
@app.get("/")
def root():
    return {"mensaje": "API de detección de puntuaciones inusuales. Usa POST /detectar-puntuacion"}

# Endpoint principal
@app.post("/detectar-puntuacion", 
            response_model=List[PunctuationError],
            summary="Detecta puntuación inusual en una oración")
def detect_punctuation(input_data: SentenceInput):
    """
    Analiza una oración en busca de errores de puntuación y devuelve una lista de los errores encontrados.
    """
    try:
        errors = analyze_punctuation(input_data.sentence)
        return errors
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))