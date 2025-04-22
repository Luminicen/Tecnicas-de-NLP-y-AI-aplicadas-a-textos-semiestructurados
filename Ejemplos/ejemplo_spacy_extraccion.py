import spacy
from spacy.matcher import Matcher

nlp = spacy.load("es_core_news_sm")
matcher = Matcher(nlp.vocab)
patron_firma = [
    {"LOWER": "firmado"},
    {"LOWER": "digitalmente"},
    {"LOWER": "por"},
    {"POS": "PROPN", "OP": "+"}  # Uno o más nombres propios
]

matcher.add("FIRMA_DIGITAL", [patron_firma])
texto = """
El documento fue revisado por el abogado. Firmado Digitalmente por juan perez.
Otra sección dice: Firmado Digitalmente por María López Fernández.
"""
doc = nlp(texto)
matches = matcher(doc)

print("Frases de firma detectadas:")
for match_id, start, end in matches:
    span = doc[start:end]
    print(f"- {span.text}")
