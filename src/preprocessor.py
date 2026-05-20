"""
Pré-processamento de séries temporais para a LSTM.

Inclui:
- Normalização com MinMaxScaler (0..1).
- Criação de janelas deslizantes (X = N dias passados, y = próximo dia).
- Persistência do scaler.
"""
import logging
from pathlib import Path
from typing import Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

logger = logging.getLogger(__name__)


def fit_scaler(values: np.ndarray) -> MinMaxScaler:
    """Treina e retorna um MinMaxScaler em valores 1D ou 2D."""
    scaler = MinMaxScaler(feature_range=(0, 1))
    if values.ndim == 1:
        values = values.reshape(-1, 1)
    scaler.fit(values)
    return scaler


def transform_with_scaler(values: np.ndarray, scaler: MinMaxScaler) -> np.ndarray:
    if values.ndim == 1:
        values = values.reshape(-1, 1)
    return scaler.transform(values)


def inverse_transform(values: np.ndarray, scaler: MinMaxScaler) -> np.ndarray:
    if values.ndim == 1:
        values = values.reshape(-1, 1)
    return scaler.inverse_transform(values).flatten()


def create_windows(
    series: np.ndarray, window_size: int
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Cria janelas deslizantes para LSTM.

    Args:
        series: array 1D ou (N, 1) com a série temporal já normalizada.
        window_size: número de timesteps por janela.

    Returns:
        X: shape (n_samples, window_size, 1)
        y: shape (n_samples,)
    """
    if series.ndim == 2:
        series = series.flatten()

    if len(series) <= window_size:
        raise ValueError(
            f"Série tem {len(series)} pontos mas window_size={window_size}. "
            "Forneça mais dados."
        )

    X, y = [], []
    for i in range(window_size, len(series)):
        X.append(series[i - window_size : i])
        y.append(series[i])

    X = np.array(X).reshape(-1, window_size, 1)
    y = np.array(y)
    return X, y


def train_test_split_time(
    X: np.ndarray, y: np.ndarray, train_ratio: float = 0.8
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Split TEMPORAL — NUNCA usar shuffle em séries temporais!
    Os primeiros X% viram treino, o resto teste.
    """
    split_idx = int(len(X) * train_ratio)
    return X[:split_idx], X[split_idx:], y[:split_idx], y[split_idx:]


def prepare_dataset(
    closes: pd.Series,
    window_size: int,
    train_ratio: float = 0.8,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, MinMaxScaler]:
    """
    Pipeline completa: normaliza, gera janelas, divide treino/teste.

    Returns:
        X_train, X_test, y_train, y_test, scaler
    """
    values = closes.values.reshape(-1, 1).astype(np.float32)

    # Ajusta scaler APENAS no conjunto de treino para evitar data leakage
    split_idx = int(len(values) * train_ratio)
    scaler = fit_scaler(values[:split_idx])
    scaled = transform_with_scaler(values, scaler)

    X, y = create_windows(scaled, window_size=window_size)
    X_train, X_test, y_train, y_test = train_test_split_time(X, y, train_ratio)

    logger.info(
        "Dataset pronto: X_train=%s | X_test=%s | window=%d",
        X_train.shape, X_test.shape, window_size,
    )
    return X_train, X_test, y_train, y_test, scaler


def save_scaler(scaler: MinMaxScaler, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(scaler, path)
    logger.info("Scaler salvo em %s", path)


def load_scaler(path: str) -> MinMaxScaler:
    return joblib.load(path)
