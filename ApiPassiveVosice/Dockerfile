# Usamos una imagen base de Python
FROM python:3.12-slim

# Evitamos que Python genere archivos .pyc y buffers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecemos el directorio de trabajo
WORKDIR /app

# Copiamos los archivos del proyecto
COPY . /app

# Instalamos pip actualizando y las dependencias
RUN pip install --upgrade pip
RUN pip install fastapi pydantic spacy "uvicorn[standard]"

# Descargamos el modelo de spaCy en español
RUN python -m spacy download es_core_news_sm

# Exponemos el puerto que usará la API
EXPOSE 8000

# Comando para correr la API con Uvicorn
CMD ["uvicorn", "api_pasiva:app", "--host", "0.0.0.0", "--port", "8000"]
