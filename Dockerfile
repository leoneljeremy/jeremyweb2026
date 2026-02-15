FROM python:3.11-slim

WORKDIR /app

# Copiamos el archivo de requisitos e instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código
COPY . .

EXPOSE 8000

# Comando para ejecutar tu servidor (ejemplo con Gunicorn o Uvicorn)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]