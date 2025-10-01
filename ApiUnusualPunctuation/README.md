# API Detección de Puntuación Inusual (FastAPI + spaCy)

Este proyecto implementa una API en **FastAPI** que detecta errores de puntuación inusuales en oraciones en español, utilizando el modelo lingüístico de **spaCy** (`es_core_news_sm`).

---

## 📌 Funcionalidades
- Detecta errores de mayúsculas/minúsculas, como:
  - `"la carta fue escrita por Juan."`
  - `"Fui al trabajo, Y después a casa."`
- Detecta la falta de signos de apertura en exclamaciones e interrogaciones, como:
  - `"Qué día es hoy?."`
- Detecta uso excesivo o incorrecto de signos de puntuación, como:
  - `"Hola!! Cómo estás??"`
- Detecta signos de agrupación sin su pareja (paréntesis, comillas, etc.), como:
    - `"(Ella lo dijo ayer."`
- Detecta errores de espaciado alrededor de la puntuación, como:
    - `"La respuesta es sí , por supuesto."`
    - `""Llegó tarde.No dio explicaciones."`
- Para cada error detectado, se devuelve una descripción, el texto y su posición exacta.

---

## ⚙️ Instalación

1. Clonar o copiar el proyecto en tu máquina.
2. Crear un entorno virtual (opcional, recomendado):

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
    ```
## Dependencias UwU
   ```bash
   pip install -r requirements.txt
   python -m spacy download es_core_news_sm
```
## Levantar Servidor
```bash
uvicorn api_punctuation:app --reload
```
El servidor quedará disponible en: http://127.0.0.1:8000

## EndPoints
1. GET /: Prueba rápida para verificar que el servidor está corriendo.
2. POST /detectar-puntuacion: Detecta errores de puntuación inusuales.

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/detectar-puntuacion' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "sentence": "Hola!, Cómo estás?"
}'
```
```json
{
  "original": "Hola!, Cómo estás?",
  "errores": [
    {
      "posición": [5, 6],
      "texto": "!",
      "descripción": "Uso excesivo de signos de puntuación"
    },
    {
      "posición": [12, 13],
      "texto": ",",
      "descripción": "Falta de espacio después de un signo de puntuación"
    }
  ]
}
```
## TEST!
Los tests usan pytest y TestClient de FastAPI.
Esto permite probar la API sin necesidad de levantar el servidor.
Ejecutarlos posicionandose en la carpeta donde se encuentra el servidor. Caso contrario no les va a funcionar:
```bash
pytest -v
```
Tests incluidos (test_api_punctuation.py):

test_root → Verifica que el endpoint raíz responda.

test_oracion_sin_errores → Comprueba que una oración perfecta devuelva una lista vacía.

test_errores_de_capitalizacion → Valida la detección de errores de mayúsculas y minúsculas.

test_puntuacion_excesiva_y_suspensivos → Asegura que se detecte la puntuación repetida, exceptuando a los puntos suspensivos (...).

test_errores_de_espaciado → Verifica la detección de espaciado incorrecto antes y después de la puntuación.

test_falta_signos_apertura → Comprueba la detección de ! y ? sin sus signos de apertura ¡ y ¿.

test_signos_agrupacion_sin_balancear → Valida la detección de paréntesis o comillas sin su pareja de cierre.

test_oracion_con_multiples_errores → Prueba una oración compleja que contiene varios tipos de errores a la vez.

La salida de los test, si todo esta OK, va a ser:
```bash
test_api_punctuation.py::test_root PASSED
test_api_punctuation.py::test_oracion_sin_errores PASSED
test_api_punctuation.py::test_errores_de_capitalizacion PASSED
test_api_punctuation.py::test_puntuacion_excesiva_y_suspensivos PASSED
test_api_punctuation.py::test_errores_de_espaciado PASSED
test_api_punctuation.py::test_falta_signos_apertura PASSED
test_api_punctuation.py::test_signos_agrupacion_sin_balancear PASSED
test_api_punctuation.py::test_oracion_con_multiples_errores PASSED