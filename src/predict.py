"""
Módulo de inferência — carrega modelo + scaler e faz previsões.

Encapsula a lógica de previsão para reutilização tanto pela API quanto
por scripts. Suporta previsão de 1 dia ou multi-step (recursiva).
"""
import json
import logging
from pathlib import Path
from typing import List

import keras
import numpy as np

from src.preprocessor import load_scaler

logger = logging.getLogger(__name__)


class StockPredictor:
    """Encapsula o modelo, o scaler e os metadados para inferência."""

    def __init__(self, model_path: str, scaler_path: str, metadata_path: str):
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.metadata_path = metadata_path

        if not Path(model_path).exists():
            raise FileNotFoundError(
                f"Modelo não encontrado em {model_path}. "
                "Execute `python -m src.train` primeiro."
            )

        logger.info("Carregando modelo de %s", model_path)
        self.model = keras.models.load_model(model_path)

        logger.info("Carregando scaler de %s", scaler_path)
        self.scaler = load_scaler(scaler_path)

        with open(metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        self.window_size: int = self.metadata["window_size"]
        logger.info("Predictor pronto. window_size=%d", self.window_size)

    # ------------------------------------------------------------------ #
    def predict_next(self, close_prices: List[float]) -> float:
        """
        Prevê o próximo preço a partir de uma janela de close_prices.

        Args:
            close_prices: lista com pelo menos `window_size` preços de fechamento
                          em ordem cronológica (mais antigo → mais recente).

        Returns:
            Preço previsto na escala original (USD/BRL).
        """
        if len(close_prices) < self.window_size:
            raise ValueError(
                f"Forneça pelo menos {self.window_size} preços. "
                f"Recebidos: {len(close_prices)}."
            )

        # Pega apenas os últimos `window_size` valores
        window = np.array(close_prices[-self.window_size :], dtype=np.float32)
        window = window.reshape(-1, 1)

        scaled = self.scaler.transform(window)
        X = scaled.reshape(1, self.window_size, 1)

        pred_scaled = self.model.predict(X, verbose=0)
        pred = self.scaler.inverse_transform(pred_scaled).flatten()[0]
        return float(pred)

    # ------------------------------------------------------------------ #
    def predict_multistep(
        self, close_prices: List[float], steps: int = 5
    ) -> List[float]:
        """
        Previsão multi-step recursiva.

        Cada novo preço previsto é adicionado à janela para prever o seguinte.
        Atenção: erros se acumulam quanto maior o `steps`.
        """
        if steps < 1:
            raise ValueError("`steps` deve ser >= 1.")

        history = list(close_prices[-self.window_size :])
        predictions: List[float] = []

        for _ in range(steps):
            next_pred = self.predict_next(history)
            predictions.append(next_pred)
            history.append(next_pred)

        return predictions
