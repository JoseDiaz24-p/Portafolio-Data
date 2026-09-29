FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Evitar archivos .pyc y permitir logs inmediatos
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del proyecto
COPY src/ ./src/
COPY tests/ ./tests/
COPY run_pipeline.py .
COPY pytest.ini .

# Ejecutar el pipeline
CMD ["python", "run_pipeline.py"]