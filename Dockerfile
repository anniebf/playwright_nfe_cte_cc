FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

ENV PYTHONUNBUFFERED=1 \
    HEADLESS=true \
    DOWNLOADS_DIR=/data/downloads \
    LOG_DIR=/data/log \
    DESTINO_FISCAL=/data/saida/FISCAL \
    DESTINO_CC="/data/saida/Conta Corrente" \
    PARAMS_JSON=/run/secrets/params.json

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./

# Credenciais (.env com usernameBd, passwordBd, dsn, token) e params.json devem ser injetados em runtime
CMD ["python", "main.py"]
