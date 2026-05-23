"""
Módulo de inferência — carrega modelo + scaler e faz previsões.

Encapsula a lógica de previsão para reutilização tanto pela API quanto
por scripts. Suporta previsão de 1 dia ou multi-step (recursiva).
Inclui ModelRegistry para servir múltiplos tickers simultaneamente.
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


class ModelRegistry:
    """Carrega e mantém em cache um StockPredictor por ticker.

    Busca modelos em ``models/{SYMBOL}/`` e cai de volta ao diretório
    plano ``models/`` (modelo legado / padrão) quando não há subpasta.
    """

    def __init__(self, models_dir: str | Path, default_symbol: str) -> None:
        self._dir = Path(models_dir)
        self._default_symbol = default_symbol.upper()
        self._cache: dict[str, StockPredictor] = {}

    # ------------------------------------------------------------------ #
    def get(self, symbol: str) -> "StockPredictor":
        key = symbol.upper()
        if key not in self._cache:
            self._cache[key] = self._load(key)
        return self._cache[key]

    def _load(self, symbol: str) -> StockPredictor:
        sym_dir = self._dir / symbol
        if sym_dir.is_dir() and (sym_dir / "lstm_model.keras").exists():
            return StockPredictor(
                model_path=str(sym_dir / "lstm_model.keras"),
                scaler_path=str(sym_dir / "scaler.pkl"),
                metadata_path=str(sym_dir / "metadata.json"),
            )
        # Fallback: flat models/ directory (modelo padrão / legado)
        flat = self._dir / "lstm_model.keras"
        if flat.exists():
            logger.info(
                "Modelo por símbolo não encontrado para %s — usando modelo padrão.",
                symbol,
            )
            return StockPredictor(
                model_path=str(flat),
                scaler_path=str(self._dir / "scaler.pkl"),
                metadata_path=str(self._dir / "metadata.json"),
            )
        raise FileNotFoundError(
            f"Nenhum modelo encontrado para {symbol}. "
            "Execute `python scripts/train_all.py` para treinar."
        )

    # ------------------------------------------------------------------ #
    def list_available(self) -> list[str]:
        """Retorna símbolos com modelo treinado em subpastas de models/."""
        return [
            d.name
            for d in sorted(self._dir.iterdir())
            if d.is_dir() and (d / "lstm_model.keras").exists()
        ]

    # ------------------------------------------------------------------ #
    @property
    def default(self) -> StockPredictor:
        return self.get(self._default_symbol)
