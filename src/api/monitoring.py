"""
Métricas Prometheus customizadas para monitorar o modelo em produção.
"""
import time

from prometheus_client import Counter, Gauge, Histogram

# ----- Contadores ------------------------------------------------- #
PREDICTIONS_TOTAL = Counter(
    "predictions_total",
    "Total de previsões realizadas",
    ["endpoint", "status"],
)

PREDICTION_ERRORS = Counter(
    "prediction_errors_total",
    "Total de erros durante previsões",
    ["error_type"],
)

# ----- Histogramas ------------------------------------------------ #
PREDICTION_DURATION = Histogram(
    "prediction_duration_seconds",
    "Tempo de inferência do modelo em segundos",
    ["endpoint"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

# ----- Gauges ----------------------------------------------------- #
MODEL_LOADED = Gauge(
    "model_loaded",
    "1 se o modelo está carregado, 0 caso contrário",
)

LAST_PREDICTION_VALUE = Gauge(
    "last_prediction_value",
    "Último valor previsto pela API",
    ["symbol"],
)


class TrackPrediction:
    """Context manager para medir tempo e registrar métricas de previsão."""

    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.start: float = 0.0

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.perf_counter() - self.start
        PREDICTION_DURATION.labels(endpoint=self.endpoint).observe(duration)
        if exc_type is None:
            PREDICTIONS_TOTAL.labels(endpoint=self.endpoint, status="success").inc()
        else:
            PREDICTIONS_TOTAL.labels(endpoint=self.endpoint, status="error").inc()
            PREDICTION_ERRORS.labels(error_type=exc_type.__name__).inc()
        return False  # propaga exceção
