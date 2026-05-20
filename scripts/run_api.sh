#!/usr/bin/env bash
# Sobe a API local em modo desenvolvimento (com hot-reload).
set -euo pipefail

uvicorn src.api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload
