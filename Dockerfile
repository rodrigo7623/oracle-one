FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY docs/ docs/
COPY static/ static/
COPY scripts/ scripts/

# El índice FAISS se genera en build time para que el contenedor arranque
# listo para responder, sin depender de una clave de Anthropic en ese paso
# (los embeddings son locales, no llaman a ninguna API externa).
RUN python -m app.ingest

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
