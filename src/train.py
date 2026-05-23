"""
Script de treinamento end-to-end.

Uso:
    python -m src.train
    python -m src.train --symbol PETR4.SA --epochs 30
"""
import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from src.config import settings
from src.data_loader import fetch_stock_data, get_close_prices
from src.evaluate import compute_metrics, print_metrics
from src.model import build_lstm_model, get_callbacks
from src.preprocessor import (
    inverse_transform,
    prepare_dataset,
    save_scaler,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("train")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Treina o modelo LSTM.")
    parser.add_argument("--symbol", default=settings.DEFAULT_SYMBOL)
    parser.add_argument("--start", default=settings.DEFAULT_START_DATE)
    parser.add_argument("--end", default=settings.DEFAULT_END_DATE)
    parser.add_argument("--window", type=int, default=settings.WINDOW_SIZE)
    parser.add_argument("--epochs", type=int, default=settings.EPOCHS)
    parser.add_argument("--batch-size", type=int, default=settings.BATCH_SIZE)
    parser.add_argument("--lr", type=float, default=settings.LEARNING_RATE)
    parser.add_argument(
        "--model-path", default=settings.MODEL_PATH,
        help="Caminho de saída do modelo .keras",
    )
    parser.add_argument("--scaler-path", default=settings.SCALER_PATH)
    parser.add_argument("--metadata-path", default=settings.METADATA_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Deriva paths por símbolo automaticamente quando não sobrescritos pelo usuário
    symbol_dir = Path(settings.MODELS_DIR) / args.symbol
    if args.model_path == settings.MODEL_PATH:
        args.model_path = str(symbol_dir / "lstm_model.keras")
    if args.scaler_path == settings.SCALER_PATH:
        args.scaler_path = str(symbol_dir / "scaler.pkl")
    if args.metadata_path == settings.METADATA_PATH:
        args.metadata_path = str(symbol_dir / "metadata.json")

    logger.info("=" * 60)
    logger.info(" TREINAMENTO LSTM - PREVISÃO DE PREÇO DE AÇÕES")
    logger.info("=" * 60)

    # ---------- 1. Coleta ----------
    df = fetch_stock_data(args.symbol, args.start, args.end)
    closes = get_close_prices(df)
    logger.info("Período: %s a %s | %d dias úteis", args.start, args.end, len(closes))

    # ---------- 2. Pré-processamento ----------
    X_train, X_test, y_train, y_test, scaler = prepare_dataset(
        closes,
        window_size=args.window,
        train_ratio=settings.TRAIN_SPLIT,
    )

    # ---------- 3. Modelo ----------
    model = build_lstm_model(
        window_size=args.window,
        lstm_units_1=settings.LSTM_UNITS_1,
        lstm_units_2=settings.LSTM_UNITS_2,
        dropout_rate=settings.DROPOUT_RATE,
        learning_rate=args.lr,
    )

    # ---------- 4. Treinamento ----------
    callbacks = list(get_callbacks(patience=10))
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=args.epochs,
        batch_size=args.batch_size,
        callbacks=callbacks,
        verbose=1,
        shuffle=False,  # série temporal — não embaralhar
    )

    # ---------- 5. Avaliação ----------
    y_pred_scaled = model.predict(X_test, verbose=0).flatten()
    y_pred = inverse_transform(y_pred_scaled, scaler)
    y_true = inverse_transform(y_test, scaler)

    metrics = compute_metrics(y_true, y_pred)
    print_metrics(metrics)

    # ---------- 6. Persistência ----------
    Path(args.model_path).parent.mkdir(parents=True, exist_ok=True)
    model.save(args.model_path)
    logger.info("Modelo salvo em %s", args.model_path)

    save_scaler(scaler, args.scaler_path)

    metadata = {
        "symbol": args.symbol,
        "start_date": args.start,
        "end_date": args.end,
        "window_size": args.window,
        "lstm_units_1": settings.LSTM_UNITS_1,
        "lstm_units_2": settings.LSTM_UNITS_2,
        "dropout_rate": settings.DROPOUT_RATE,
        "epochs_trained": len(history.history["loss"]),
        "batch_size": args.batch_size,
        "learning_rate": args.lr,
        "train_samples": int(X_train.shape[0]),
        "test_samples": int(X_test.shape[0]),
        "metrics": metrics,
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }
    Path(args.metadata_path).parent.mkdir(parents=True, exist_ok=True)
    with open(args.metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    logger.info("Metadata salvo em %s", args.metadata_path)

    logger.info("✅ Treinamento concluído.")


if __name__ == "__main__":
    main()
