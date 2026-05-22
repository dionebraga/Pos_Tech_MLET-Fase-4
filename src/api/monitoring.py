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


def initialize_metrics(symbols: list[str] | None = None) -> None:
    """Pre-inicializa label combinations para que as métricas apareçam no /metrics
    mesmo antes da primeira previsão (evita 'No data' no Grafana).

    Histogramas recebem uma observação mínima (0.001 s) para que rate() e
    histogram_quantile() retornem 0 em vez de NaN quando ainda não há previsões.
    Gauges recebem .set(0) explícito para garantir que a série existe no Prometheus.
    """
    for ep in ("/predict", "/predict/symbol"):
        PREDICTION_DURATION.labels(endpoint=ep).observe(0.001)
        PREDICTIONS_TOTAL.labels(endpoint=ep, status="success")
        PREDICTIONS_TOTAL.labels(endpoint=ep, status="error")
    PREDICTION_ERRORS.labels(error_type="ValueError")
    PREDICTION_ERRORS.labels(error_type="Exception")
    for sym in (symbols or ["AAPL", "GOOGL", "MSFT", "AMZN", "NVDA"]):
        LAST_PREDICTION_VALUE.labels(symbol=sym).set(0)


class TrackPrediction:
    """Context manager para medir tempo e registrar métricas de previsão."""

    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.start: float = 0.0

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, _exc_val, _exc_tb):
        duration = time.perf_counter() - self.start
        PREDICTION_DURATION.labels(endpoint=self.endpoint).observe(duration)
        if exc_type is None:
            PREDICTIONS_TOTAL.labels(endpoint=self.endpoint, status="success").inc()
        else:
            PREDICTIONS_TOTAL.labels(endpoint=self.endpoint, status="error").inc()
            PREDICTION_ERRORS.labels(error_type=exc_type.__name__).inc()
        return False  # propaga exceção
