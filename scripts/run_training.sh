#!/usr/bin/env bash
# Helper para rodar o treinamento.
# Uso: ./scripts/run_training.sh [SYMBOL]

set -euo pipefail

SYMBOL="${1:-AAPL}"
START="${2:-2018-01-01}"
END="${3:-2026-05-01}"
EPOCHS="${4:-50}"

echo "🧠 Treinando LSTM para $SYMBOL ($START → $END) por $EPOCHS épocas"
python -m src.train \
    --symbol "$SYMBOL" \
    --start "$START" \
    --end "$END" \
    --epochs "$EPOCHS"
