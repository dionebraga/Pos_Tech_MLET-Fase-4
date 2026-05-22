"""
Métricas de avaliação para previsão de séries temporais.

- MAE  (Mean Absolute Error)            — erro médio absoluto na unidade real
- RMSE (Root Mean Squared Error)        — penaliza mais erros grandes
- MAPE (Mean Absolute Percentage Error) — erro percentual médio
"""
from typing import Dict

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Calcula MAE, RMSE e MAPE.

    Args:
        y_true: valores reais (nao normalizados, escala original).
        y_pred: valores previstos (nao normalizados).

    Returns:
        dict com chaves 'mae', 'rmse', 'mape'.
    """
    y_true = np.asarray(y_true).flatten()
    y_pred = np.asarray(y_pred).flatten()

    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))

    # MAPE manual para evitar divisão por zero
    mask = y_true != 0
    mape = float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)

    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "mape": mape,
    }


def print_metrics(metrics: Dict[str, float]) -> None:
    print("\n" + "=" * 50)
    print("📊 MÉTRICAS DE AVALIAÇÃO")
    print("=" * 50)
    print(f"  MAE  : {metrics['mae']:.4f}")
    print(f"  RMSE : {metrics['rmse']:.4f}")
    print(f"  MAPE : {metrics['mape']:.2f}%")
    print("=" * 50 + "\n")
