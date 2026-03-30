FROM python:3.11-slim

RUN useradd -m -u 1000 user && \
    mkdir -p /home/user/data && \
    chown -R user:user /home/user

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000 \
    HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

COPY --chown=user requirements.runtime.txt ./

RUN pip install --upgrade pip && \
    pip install -r requirements.runtime.txt

COPY --chown=user app ./app
COPY --chown=user artifacts ./artifacts
COPY --chown=user scripts ./scripts
COPY --chown=user pyproject.toml README.md ./

EXPOSE 8000

USER user

CMD ["sh", "-c", "python scripts/create_db.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
