import spacy


nlp = spacy.load("es_core_news_sm")
texto = "Pedrito viajó a Madrid el lunes para reunirse con representantes de la Unión Europea."
doc = nlp(texto)
print("Tokens:")
for token in doc:
    print(f"{token.text:<15} -> {token.pos_:<10} ({token.dep_})")
print("\nEntidades nombradas:")
for ent in doc.ents:
    print(f"{ent.text:<30} - {ent.label_}")
print("\nÁrbol de dependencias:")
for token in doc:
    print(f"{token.text} <-- {token.dep_} -- {token.head.text}")
