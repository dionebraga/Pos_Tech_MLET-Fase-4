#!/usr/bin/env bash
# Helper para rodar o treinamento.
# Uso: ./scripts/run_training.sh [SYMBOL]

set -euo pipefail

SYMBOL="${1:-AAPL}"
START="${2:-2018-01-01}"
END="${3:-2024-07-20}"
EPOCHS="${4:-50}"

echo "🧠 Treinando LSTM para $SYMBOL ($START → $END) por $EPOCHS épocas"
python -m src.train \
    --symbol "$SYMBOL" \
    --start "$START" \
    --end "$END" \
    --epochs "$EPOCHS"
