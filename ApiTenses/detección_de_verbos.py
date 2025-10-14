import spacy
from spacy.matcher import Matcher

# Carga del modelo (se incluye fallback opcional)
try:
    nlp = spacy.load("es_dep_news_trf")
except OSError:
    # Fallback: >pip install es_core_news_sm
    nlp = spacy.load("es_core_news_sm")

# ------Construccion del matcher ------
matcher = Matcher(nlp.vocab)

# ---- Patrones para el matcher para verbos compuestos y perífrasis ----

# Pretérito perfecto compuesto: haber(Pres) + Part
# Ejemplo: "he comido", "has hablado"
patron_perf_comp = [
    {"LEMMA": "haber", "POS": "AUX", "MORPH": {"IS_SUPERSET": ["Tense=Pres"]}},
    {"POS": {"IN": ["ADV", "PART"]}, "OP": "*"},
    {"MORPH": {"IS_SUPERSET": ["VerbForm=Part"]}},
]
matcher.add("PERFECTO_COMPUESTO", [patron_perf_comp])


# Pretérito pluscuamperfecto: haber(Past) + Part

# Variante 1: haber con Tense=Past
patron_pluscuam_past = [
    {"LEMMA": "haber", "POS": {"IN": ["AUX", "VERB"]}, "MORPH": {"IS_SUPERSET": ["Tense=Past"]}},
    {"POS": {"IN": ["ADV", "PART", "PRON"]}, "OP": "*"},
    {"MORPH": {"IS_SUPERSET": ["VerbForm=Part"]}},
]

# Variante 2: haber con Tense=Imp (imperfecto) 
patron_pluscuam_imp = [
    {"LEMMA": "haber", "POS": {"IN": ["AUX", "VERB"]}, "MORPH": {"IS_SUPERSET": ["Tense=Imp"]}},
    {"POS": {"IN": ["ADV", "PART", "PRON"]}, "OP": "*"},
    {"MORPH": {"IS_SUPERSET": ["VerbForm=Part"]}},
]
matcher.add("PLUSCUAMPERFECTO", [patron_pluscuam_past, patron_pluscuam_imp])

# Futuro compuesto: haber(Fut) + Part
patron_fut_comp = [
    {"LEMMA": "haber", "POS": "AUX", "MORPH": {"IS_SUPERSET": ["Tense=Fut"]}},
    {"POS": {"IN": ["ADV", "PART"]}, "OP": "*"},
    {"MORPH": {"IS_SUPERSET": ["VerbForm=Part"]}},
]
matcher.add("FUTURO_COMPUESTO", [patron_fut_comp])

# Futuro perifrástico: ir(Pres) + a + Inf
patron_fut_peri = [
    {"LEMMA": "ir", "MORPH": {"IS_SUPERSET": ["Tense=Pres"]}},
    {"LOWER": "a"},
    {"MORPH": {"IS_SUPERSET": ["VerbForm=Inf"]}},
]
matcher.add("FUTURO_PERIFRASTICO", [patron_fut_peri])

# Presente progresivo: estar(Pres) + (Adv/Part)* + Ger
patron_pres_prog = [
    {"LEMMA": "estar", "MORPH": {"IS_SUPERSET": ["Tense=Pres"]}},
    {"POS": {"IN": ["ADV", "PART"]}, "OP": "*"},
    {"MORPH": {"IS_SUPERSET": ["VerbForm=Ger"]}},
]
matcher.add("PRESENTE_PROGRESIVO", [patron_pres_prog])


# -------- Función principal --------
def detectar_tiempo_verbal(texto: str):
    doc = nlp(texto)
    resultados = []

    # Tiempos simples con analisis morfológico
    for i, token in enumerate(doc):
        if token.pos_ in {"VERB", "AUX"}:
            if token.morph.get("VerbForm") != ["Fin"]:
                continue  # Solo verbos finitos (no verboides)

            # Evitar 'haber' si viene seguido de participio (lo maneja el matcher)
            if token.lemma_ == "haber" and i + 1 < len(doc) and "Part" in doc[i+1].morph.get("VerbForm"):
                continue

            tense = token.morph.get("Tense")
            if "Past" in tense:
                resultados.append((token.text, "Pasado simple/Imperfecto"))
            if "Pres" in tense and token.pos_ == "VERB":
                resultados.append((token.text, "Presente"))
            if "Fut" in tense:
                resultados.append((token.text, "Futuro simple"))

    # Tiempos compuestos y perífrasis con matcher
    for match_id, start, end in matcher(doc):
        span = doc[start:end]
        label = nlp.vocab.strings[match_id]
        if label == "PERFECTO_COMPUESTO":
            resultados.append((span.text, "Pretérito perfecto compuesto"))
        elif label == "PLUSCUAMPERFECTO":
            resultados.append((span.text, "Pretérito pluscuamperfecto"))
        elif label == "FUTURO_COMPUESTO":
            resultados.append((span.text, "Futuro compuesto"))
        elif label == "FUTURO_PERIFRASTICO":
            resultados.append((span.text, "Futuro perifrástico"))
        elif label == "PRESENTE_PROGRESIVO":
            resultados.append((span.text, "Presente progresivo"))

    # Eliminación de duplicados (mismo verbo por ambos metodos o solapaciones de matcher)
    vistos = set()
    resultados_unicos = []
    for expr, etq in resultados:
        clave = (expr, etq)
        if clave not in vistos:
            vistos.add(clave)
            resultados_unicos.append(clave)

    return resultados_unicos or []



# Para testeos se puede ejecutar como main:
if __name__ == "__main__":
    if len(sys.argv)<1:
        print("Uso: python main.py arg1 ")
        sys.exit(1)


    texto = "".join(sys.argv[1:]) 
    print(verificacion(texto))