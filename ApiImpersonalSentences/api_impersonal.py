from fastapi import FastAPI
from pydantic import BaseModel
import spacy
from typing import Tuple

# Cargamos el modelo de spaCy
nlp = spacy.load("es_core_news_sm")

# FastAPI app
app = FastAPI(title="Detector de Oraciones Impersonales", version="1.1")

# Modelo de entrada
class TextoEntrada(BaseModel):
    texto: str

# helpers
def _has_explicit_subject(verb_token):
    """Devuelve True si el verbo tiene un sujeto explícito dependiente (nsubj, csubj, etc.)."""
    subj_deps = {"nsubj", "nsubj:pass", "csubj", "csubj:pass", "expl"}
    for child in verb_token.children:
        if child.dep_ in subj_deps:
            return True
    return False

def _clausal_has_subject(span):
    """Revisa si en un span/cláusula existe un sujeto explícito (heurística)."""
    for t in span:
        if t.dep_ in {"nsubj", "nsubj:pass", "csubj"}:
            return True
    return False

def detectar_impersonal_spacy(texto: str) -> Tuple[bool, str]:
    """
    Detecta si la oración es impersonal usando únicamente análisis spaCy (dep parse, lemas, morph, ents).
    Devuelve (es_impersonal: bool, motivo: str).
    Reglas (heurísticas sintácticas):
      - 'hay' (haber en forma de existencia) -> impersonal.
      - 'se' ligado al verbo: si hay nsubj nominal -> impersonal (pasiva/impersonal).
        si no hay nsubj pero hay obj -> reflexivo/transitivo -> NO impersonal.
      - 'ser' copulativo + predicado adjetival sin sujeto explícito -> impersonal (Es necesario...).
      - 'hacer' sin sujeto explícito y sin patrón temporal -> impersonal (Hace frío).
      - verbo finito en 3ª persona sin sujeto explícito en su cláusula -> impersonal.
    """
    texto = (texto or "").strip()
    if not texto:
        return False, "texto vacío"

    doc = nlp(texto)

    # 1) "hay" (haber en forma de existencia)
    for t in doc:
        if t.lemma_.lower() == "haber" and t.text.lower() == "hay":
            return True, "construcción de existencia: 'hay' (haber en forma de existencia)"

    # obtenemos los posibles verbos principales (raíces de cláusulas)
    root_verbs = [t for t in doc if t.dep_ == "ROOT" and t.pos_ in {"VERB", "AUX"}]
    if not root_verbs:
        root_verbs = [t for t in doc if t.pos_ in {"VERB", "AUX"}]

    # Evaluamos cada verbo candidato
    for verb in root_verbs:
        # Si el verbo tiene sujeto explícito, descartamos según ese verbo
        if _has_explicit_subject(verb):
            continue

        # ----- "se" impersonal / reflexivo -----
        # Buscamos tokens "se" cuyo head sea este verbo
        se_tokens = [t for t in doc if t.text.lower() == "se" and t.head == verb and t.pos_ == "PRON"]
        if se_tokens:
            # Si el verbo tiene sujeto nominal (nsubj) -> pasiva/impersonal: TRUE
            has_nsubj = any(child.dep_ in {"nsubj", "nsubj:pass"} for child in verb.children)
            # Si el verbo tiene objeto directo -> probablemente reflexivo/transitivo -> NO impersonal
            has_obj = any(child.dep_ in {"obj", "dobj", "iobj", "obl", "ccomp", "xcomp"} for child in verb.children)
            # Si hay agente explícito introducido por 'por', preferimos no considerarlo impersonal
            has_por_agent = any((t.dep_ == "case" and t.lemma_ == "por") or (t.text.lower() == "por") for t in doc)

            if has_nsubj and not has_por_agent:
                return True, "construcción con 'se' + nsubj -> pasiva/impersonal (ej. 'Se venden coches...')"
            if not has_nsubj and has_obj:
                # ejemplo: "Se comió la manzana." -> reflexivo/transitivo -> NO impersonal
                return False, "construcción con 'se' + objeto directo -> reflexiva/transitiva (no impersonal)"
            # caso intermedio (p. ej. 'No se permite fumar...') -> marcar impersonal
            if not has_por_agent:
                return True, "construcción con 'se' ligada al verbo sin agente explícito -> impersonal/pasiva refleja"

        # ----- 'ser' copulativo con predicado adjetival -----
        if verb.lemma_.lower() == "ser":
            has_adj_pred = any(child.pos_ == "ADJ" or child.dep_ in {"acomp", "xcomp", "attr"} for child in verb.children)
            clause_span = list(verb.subtree)
            if has_adj_pred and not _clausal_has_subject(clause_span):
                return True, "copula 'ser' + adjetivo sin sujeto explícito -> construcción impersonal ('Es ...')"

        # ----- 'hacer' impersonal: distinguir de patrón temporal -----
        if verb.lemma_.lower() == "hacer":
            has_date_ent = any(ent.label_ in {"DATE", "TIME"} for ent in doc.ents)
            temporal_tokens = {"año", "años", "mes", "meses", "día", "días", "semana", "semanas", "hora", "horas"}
            is_temporal_pattern = False
            right = [t for t in doc[verb.i+1: verb.i+4]]
            if right and right[0].like_num:
                if len(right) > 1 and right[1].lemma_.lower() in temporal_tokens:
                    is_temporal_pattern = True
            if not has_date_ent and not is_temporal_pattern:
                return True, "verbo 'hacer' sin sujeto explícito y no patrón temporal -> impersonal (ej. 'Hace frío')"
            else:
                continue

        # ----- caso general: verbo finito en 3ª persona sin sujeto explícito -----
        person = verb.morph.get("Person")
        has_person_3 = False
        if person:
            # person es una tupla/lista de strings (ej. ('3',))
            for p in person:
                if isinstance(p, str) and p.startswith("3"):
                    has_person_3 = True
        # Consideramos impersonal solo si:
        #  - el verbo indica 3ª persona, o
        #  - no hay información de persona (person == []) pero verbo es ROOT y no hay sujeto en la cláusula
        clause_span = list(verb.subtree)
        if (has_person_3) or (not person and verb.dep_ == "ROOT"):
            if not _clausal_has_subject(clause_span):
                return True, "verbo finito (3ª persona o ROOT sin info de persona) sin sujeto explícito en la cláusula -> impersonal"

    # Si no detectamos patrón impersonal
    return False, "no se detectaron construcciones impersonales sintácticas con spaCy"
    

# Endpoint principal: POST /detectar
@app.post("/detectar")
def detectar(entrada: TextoEntrada):
    imp, motivo = detectar_impersonal_spacy(entrada.texto)
    return {"original": entrada.texto, "impersonal": imp, "motivo": motivo}

# Endpoint de prueba
@app.get("/")
def root():
    return {"mensaje": "API Detector de oraciones impersonales. Usa POST /detectar con JSON { 'texto': '...' }"}
