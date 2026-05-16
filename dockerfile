# =========================================================
# STELLA — Dockerfile
# =========================================================

FROM python:3.11-slim

# ─────────────────────────────────────────────
# Variables environnement
# ─────────────────────────────────────────────

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# ─────────────────────────────────────────────
# Dépendances système
# ─────────────────────────────────────────────

RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ─────────────────────────────────────────────
# Dossier de travail
# ─────────────────────────────────────────────

WORKDIR /app

# ─────────────────────────────────────────────
# Copie requirements
# ─────────────────────────────────────────────

COPY requirements.txt .

# ─────────────────────────────────────────────
# Installation Python
# ─────────────────────────────────────────────

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

# ─────────────────────────────────────────────
# Copie projet
# ─────────────────────────────────────────────

COPY . .

# ─────────────────────────────────────────────
# Streamlit config
# ─────────────────────────────────────────────

RUN mkdir -p /root/.streamlit

RUN echo "\
[server]\n\
headless = true\n\
port = 8501\n\
address = '0.0.0.0'\n\
enableCORS = false\n\
enableXsrfProtection = false\n\
" > /root/.streamlit/config.toml

# ─────────────────────────────────────────────
# Exposition port
# ─────────────────────────────────────────────

EXPOSE 8501

# ─────────────────────────────────────────────
# Commande lancement
# ─────────────────────────────────────────────

CMD ["streamlit", "run", "interface/app.py"]