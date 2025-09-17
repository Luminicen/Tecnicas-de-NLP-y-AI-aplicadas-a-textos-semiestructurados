from fastapi import FastAPI
import spacy

app = FastAPI()
nlp = spacy.load("es_core_news_md")  # Modelo con vectores

PREFIJOS = {"in", "im", "i", "des"}

#No existen más de 32 palabras con los prefijos mencionados que no sean abstractas

PALABRAS_EXCLUIDAS = {
    "ser", "estar", "tener", "haber", "poder", "deber", "hacer", "decir","ver", "dar", "saber", "querer", "llegar", "pasar", 
    "poner", "inodoro","invernadero","insecto","ingrediente","instrumento","inhalador", "invernáculo","indicador","imán",
    "impresora","impermeable","implante", "impulsor","impactador","iglú","ilex","isla","desarmadero","desierto", "desayuno",
    "desagüe","desnivel","desfiladero","desván","desmontable", "desbrozadora","deshielo","deslizadero","desecho","desagregado",
    "desecador"
}

PALABRAS_ABSTRACTAS_REF = [ "agradable","alegría","amar","amistad","amor","angustia","aprendizaje","bello","belleza","bien",
    "bondad","calma","cariño","caos","compasión","conciencia", "conocimiento","creación","creatividad","culpa","decisión",
    "desesperación", "destrucción","dignidad","dolor","empatía","esencial","esperanza","ética", "eternidad","fantasía","fe",
    "fealdad","felicidad","feo","fin","fortuna", "gratitud","hermoso","honestidad","honor","humildad","ilusión",
    "justicia","libertad","lindo", "lealtad","maldad","mal","memoria","malo",
    "misterio","muerte","nacimiento", "odio","orden","origen","paciencia","paz","perfección","piedad","placer", "principio",
    "realidad","respeto","responsabilidad","ruido","sabiduría", "silencio","sinceridad","soledad","solidaridad","suerte",
    "sueño","temor", "terror","tolerancia","tranquilidad","tristeza","valentía","valiente","vida","virtud","voluntad","verdad"
]


UMBRAL_SIMILITUD = 0.6  # umbral de similitud semántica

@app.get("/abstractas/")
def abstractas(texto: str):
    doc = nlp(texto)
    respuesta = []

    for token in doc:
        lemma = token.lemma_.lower()

        prefijo_valido = any(lemma.startswith(prefijo) for prefijo in PREFIJOS)

        cumple = (
            not token.is_stop
            and not token.ent_type_
            and lemma not in PALABRAS_EXCLUIDAS
            and len(lemma) > 2
        )

        # Sustantivos y verbos
        if token.pos_ in {"NOUN", "VERB"} and cumple:
            if prefijo_valido:
                respuesta.append(token.text)
            else:
                lemma_token = nlp(lemma)[0]
                for ref in PALABRAS_ABSTRACTAS_REF:
                    ref_token = nlp(ref)[0]
                    if lemma_token.has_vector and ref_token.has_vector and lemma_token.similarity(ref_token) > UMBRAL_SIMILITUD:
                        respuesta.append(token.text)
                        break

        # Adjetivos: solo abstractos mediante similitud
        elif token.pos_ == "ADJ" and cumple:
            lemma_token = nlp(lemma)[0]
            for ref in PALABRAS_ABSTRACTAS_REF:
                ref_token = nlp(ref)[0]
                if lemma_token.has_vector and ref_token.has_vector and lemma_token.similarity(ref_token) > UMBRAL_SIMILITUD:
                    respuesta.append(token.text)
                    break

    return {"respuesta": list(set(respuesta))}
