# API Conversor de Voz Pasiva a Activa (FastAPI + spaCy)

Este proyecto implementa una API en **FastAPI** que convierte oraciones en **voz pasiva** a **voz activa** en español, utilizando el modelo lingüístico de **spaCy** (`es_core_news_sm`).

---

## 📌 Funcionalidades
- Detecta oraciones en voz pasiva con estructuras como:
  - "La carta fue escrita por Juan."
  - "Los libros fueron leídos por los estudiantes."
- Convierte la oración a voz activa:
  - `"Juan escribir carta."`
  - `"Los estudiantes leer libros."`
- Si la oración ya está en voz activa o no se reconoce como pasiva → se devuelve igual.

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
uvicorn api_pasiva:app --reload
```
El servidor quedará disponible en: http://127.0.0.1:8000

## EndPoints
1. GET /: Prueba rápida para verificar que el servidor está corriendo.
2. POST /convertir: Convierte una oración de pasiva a activa.

```bash
curl -X POST "http://127.0.0.1:8000/convertir" \
     -H "Content-Type: application/json" \
     -d '{"texto": "La carta fue escrita por Juan."}'
```
```json
{
  "original": "La carta fue escrita por Juan.",
  "activa": "Juan escribir carta."
}
```
## TEST!
Los tests usan pytest y TestClient de FastAPI.
Esto permite probar la API sin necesidad de levantar el servidor.
Ejecutarlos posicionandose en la carpeta donde se encuentra el servidor. Caso contrario no les va a funcionar:
```bash
pytest -v
```
Tests incluidos (test_api.py):

test_root → Verifica que el endpoint raíz responda.

test_convertir_pasiva_simple → Convierte una oración pasiva simple.

test_convertir_pasiva_plural → Convierte oración pasiva en plural.

test_oracion_activa_no_cambia → Verifica que una oración activa no se modifique.

test_convertir_pasiva_maiev → Caso: "Los libros fueron escritos por Maiev." debe convertirse a voz activa.

La salida de los test, si todo esta OK, va a ser:
```bash
test_api.py::test_root PASSED
test_api.py::test_convertir_pasiva_simple PASSED
test_api.py::test_convertir_pasiva_plural PASSED
test_api.py::test_oracion_activa_no_cambia PASSED
test_api.py::test_convertir_pasiva_maiev PASSED
