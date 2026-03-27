FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

COPY requirements.txt ./

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY app ./app
COPY artifacts ./artifacts
COPY data ./data
COPY scripts ./scripts
COPY pyproject.toml README.md ./

EXPOSE 8000

CMD ["sh", "-c", "python scripts/create_db.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
