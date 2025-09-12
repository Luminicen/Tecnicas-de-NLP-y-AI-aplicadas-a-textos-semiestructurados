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
    "E001": "Uso incorrecto de mayúsculas después de coma",
    "E002": "Uso excesivo de signos de puntuación",
    "E003": "Espacio incorrecto antes de un signo de puntuación",
    "E004": "Falta de espacio después de un signo de puntuación",
    "E005": "Signo sin pareja (exclamación, interrogación, paréntesis, corchetes, llaves)",
}

def _create_error_dict(code: str, span: Tuple[int, int], text: str) -> Dict[str, Any]:

    #TO DO: Agregar más casos de error y descripciones detalladas

    """Crea un diccionario de error estandarizado."""
    return {
        "posición": span,
        "texto": text[span[0]:span[1]],
        "descripción": ERROR_DESCRIPTIONS.get(code, "Error desconocido")
    }

def find_incorrect_capitalization(doc: spacy.tokens.Doc, original_text: str) -> List[Dict]:
    
    #TO DO: Agregar detección de errores de minúsculas/mayúsculas generales

    """Detecta mayúsculas incorrectas después de una coma."""
    errors = []
    for token in doc[1:]:
        prev_token = doc[token.i - 1]
        if prev_token.text == "," and token.text[0].isupper() and token.pos_ not in ["PROPN"]:
            start_pos = prev_token.idx
            end_pos = token.idx + len(token.text)
            errors.append(_create_error_dict("E001", (start_pos, end_pos), original_text))
    return errors

def find_excessive_punctuation(text: str) -> List[Dict]:

    #TO DO: Agregar más casos, ver a partir de cuántos signos se considera excesivo

    """Detecta signos de puntuación repetidos excesivamente."""
    errors = []
    pattern = re.compile(r"([!?.])\1{2,}|(,){2,}")
    for match in pattern.finditer(text):
        errors.append(_create_error_dict("E002", match.span(), text))
    return errors

def find_spacing_errors(text: str) -> List[Dict]:

    #TO DO: Agregar más casos, como espacios antes de comillas, paréntesis, etc.

    """Detecta errores de espaciado alrededor de la puntuación."""
    errors = []
    pattern_before = re.compile(r"(?<=\w)\s+[.,!?;:]")
    for match in pattern_before.finditer(text):
        start, end = match.span()
        errors.append(_create_error_dict("E003", (start + 1, end), text))

    pattern_after = re.compile(r"[.,!?;:](?=[a-zA-ZáéíóúÁÉÍÓÚ])")
    for match in pattern_after.finditer(text):
        errors.append(_create_error_dict("E004", match.span(), text))
    return errors
    
def find_unbalanced_marks(text: str) -> List[Dict]:
    
    #TO DO: Agregar comillas al análisis, separar errores por tipo más claramente

    """Detecta signos de exclamación, interrogación, paréntesis, corchetes o llaves que falte abrir o cerrar."""
    errors = []
    stack = []
    opening_brackets = "([{¡¿"
    closing_brackets = ")]}!?"
    bracket_map = {')': '(', ']': '[', '}': '{', '!': '¡', '?': '¿'}

    for i, char in enumerate(text):
        if char in opening_brackets:
            stack.append((char, i))
        elif char in closing_brackets:
            if not stack or stack[-1][0] != bracket_map[char]:
                errors.append(_create_error_dict("E005", (i, i + 1), text))
            else:
                stack.pop()
    
    for char, i in stack:
        errors.append(_create_error_dict("E005", (i, i + 1), text))
    return errors

def analyze_punctuation(text: str) -> List[Dict[str, Any]]:
    """Función principal que orquesta todas las detecciones."""
    if not nlp:
        raise RuntimeError("El modelo de SpaCy no está cargado. Ejecuta 'python -m spacy download es_core_news_sm'")

    doc = nlp(text)
    all_errors = []

    all_errors.extend(find_incorrect_capitalization(doc, text))
    all_errors.extend(find_excessive_punctuation(text))
    all_errors.extend(find_spacing_errors(text))
    all_errors.extend(find_unbalanced_marks(text))

    return sorted(all_errors, key=lambda x: x['posición'][0])


app = FastAPI(
    title="Servicio de Detección de Puntuaciones Inusuales",
    description="API para analizar y detectar puntuaciones inusuales en oraciones en español.",
    version="1.0.0" 
)

class SentenceInput(BaseModel):
    sentence: str = Field(..., min_length=1, example="Hola!, Cómo estás?", description="La oración que se desea analizar.")

class PunctuationError(BaseModel):
    posición: tuple[int, int]
    texto: str
    descripción: str

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