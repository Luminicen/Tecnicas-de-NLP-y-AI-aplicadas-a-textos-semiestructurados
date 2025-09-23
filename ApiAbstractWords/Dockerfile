# Usamos una imagen base de Python
FROM python:3.12-slim

# Evitamos que Python genere archivos .pyc y buffers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecemos el directorio de trabajo
WORKDIR /app

# Copiamos solo el archivo de dependencias primero para aprovechar cache
COPY requirements.txt /app/

# Instalamos pip y dependencias
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    python -m spacy download es_core_news_sm

# Copiamos el resto del proyecto
COPY . /app

# Exponemos el puerto de la API
EXPOSE 8000

# Comando para correr la API con Uvicorn
CMD ["uvicorn", "api_pasiva:app", "--host", "0.0.0.0", "--port", "8000"]