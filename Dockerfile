FROM python:3.13-slim

WORKDIR /app

# Instalar dependencias del sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requerimientos e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente completo
COPY . .

# Generar y verificar la base de datos de semillas oficiales
RUN python scripts/generate_seed_parameters.py && python scripts/verify_data.py

# Exponer el puerto
EXPOSE 8000

ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Comando de inicio
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
