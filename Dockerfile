# =========================================================== #
# Stage 1 — Builder: instala dependências num venv isolado
# =========================================================== #
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Dependências de sistema necessárias para algumas libs
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip && pip install -r requirements.txt


# =========================================================== #
# Stage 2 — Runtime: imagem final enxuta
# =========================================================== #
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Usuário não-root (boas práticas de segurança)
RUN groupadd --system app && useradd --system --gid app --create-home app

WORKDIR /app

# Copia o venv pronto
COPY --from=builder /opt/venv /opt/venv

# Copia o código
COPY --chown=app:app src/ ./src/
COPY --chown=app:app models/ ./models/

# Baixa o modelo do Hugging Face Model Hub
RUN pip install huggingface_hub -q && \
    python -c "
from huggingface_hub import hf_hub_download
import os

repo = 'dionebraga/lstm-stock-model'
files = ['lstm_model.keras', 'scaler.pkl', 'metadata.json']
for f in files:
    path = hf_hub_download(repo_id=repo, filename=f, local_dir='models/', force_download=True)
    print(f'Downloaded {f}')
print('Model download complete')
"

USER app

EXPOSE 8000

# Healthcheck simples
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

CMD uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}
