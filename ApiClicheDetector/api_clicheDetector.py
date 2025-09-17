from rapidfuzz import fuzz
import spacy





cliches= [
    "quiero poder",
    "Para poder usar el sistema",
    "quiero administrar",
    "quiero un sistema fácil de usar",
    "Quiero poder hacer clic en un botón",
    "Para mejorar la experiencia del usuario",
    "Para aumentar la productividad",
    "Para que sea más rápido y fácil",
    "Para que funcione mejor",
    "Para que sea más intuitivo",
    "quiero gestionar todo el sistema",
    "quiero guardar datos en la base de datos",
    "quiero refactorizar el código",
    "quiero implementar la API",
    "quiero probar el sistema",
    "quiero que sea más bonito",
    "quiero un diseño moderno",
    "quiero que sea seguro",
    "quiero que sea escalable",
    "quiero poder exportar todo",
    "quiero acceder a todo desde cualquier lugar",
    "quiero que nunca falle",
    "quiero que cargue rápido",
    "quiero que sea compatible con todo",
    "quiero que siempre funcione",
    "quiero que nunca falle"
    "quiero que no tenga errores",
    "quiero que la base de datos guarde la información",
    "quiero conectarme al servidor",
    "quiero administrar usuarios y permisos",
    "quiero una aplicación que sea la mejor",
    "quiero que sea más eficiente",
    "quiero personalizar todo",
    "quiero una interfaz atractiva",
    "quiero simplicidad",
    "quiero que sea todo más claro",
    "quiero que se integre con cualquier cosa",
    "quiero que sea moderno y actual",
    "quiero que el sistema haga todo automáticamente"
  ]


app = FastAPI()

nlp = spacy.load("es_dep_news_trf")

def lematizar(texto, nlp):
    doc = nlp(texto.lower())
    return " ".join([token.lemma_ for token in doc if not token.is_punct]   )

def detectar_fuzzy(texto, lista_cliches, nlp, umbral=70):
    texto_lemmas = lematizar(texto, nlp)
    
    encontrados = []
    for cliche in lista_cliches:
        cliche_lemmas = lematizar(cliche, nlp)
        valor = fuzz.partial_ratio(cliche_lemmas, texto_lemmas)
        
        if valor >= umbral:
            print(valor)
            encontrados.append(cliche)

    if len(encontrados) == 0:
        return "No se encontraron cliches"
    return encontrados

texto = "Como tester, quiero ser capaz de ejecutar pruebas automáticas en diferentes entornos y con distintos volúmenes de datos, para que el sistema sea compatible con todo, más robusto y nunca falle en producción"
print(detectar_fuzzy(texto, cliches, nlp))