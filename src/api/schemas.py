"""
Schemas Pydantic v2 para validação de entrada/saída da API.
"""
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ============================================================ #
# Requests
# ============================================================ #
class PredictRequest(BaseModel):
    """Predição a partir de uma série já fornecida pelo cliente."""

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "close_prices": [150.0, 151.2, 149.8, 152.5, 153.1, 154.0, 152.8, 151.5,
                             153.3, 155.0, 156.2, 157.1, 155.8, 156.5, 158.0, 159.2,
                             157.5, 156.8, 158.5, 160.0, 161.1, 159.8, 160.5, 162.0,
                             163.2, 161.5, 162.8, 164.0, 165.1, 163.8, 164.5, 166.0,
                             167.2, 165.5, 166.8, 168.0, 169.1, 167.8, 168.5, 170.0,
                             171.2, 169.5, 170.8, 172.0, 173.1, 171.8, 172.5, 174.0,
                             175.2, 173.5, 174.8, 176.0, 177.1, 175.8, 176.5, 178.0,
                             179.2, 177.5, 178.8, 180.0],
            "days_ahead": 5,
        }
    })

    close_prices: List[float] = Field(
        ...,
        min_length=1,
        description=(
            "Lista de preços de fechamento em ordem cronológica. "
            "Deve conter pelo menos `window_size` valores (60 por default)."
        ),
    )
    days_ahead: int = Field(
        default=1, ge=1, le=30,
        description="Número de dias futuros a prever (1 a 30).",
    )

    @field_validator("close_prices")
    @classmethod
    def positive_prices(cls, v: List[float]) -> List[float]:
        if any(p <= 0 for p in v):
            raise ValueError("Todos os preços devem ser > 0.")
        return v


class SymbolPredictRequest(BaseModel):
    """Predição buscando histórico recente do yfinance."""

    model_config = ConfigDict(json_schema_extra={
        "example": {"symbol": "AAPL", "days_ahead": 5}
    })

    symbol: str = Field(
        ...,
        min_length=1, max_length=15,
        description="Ticker da empresa (ex: AAPL, PETR4.SA).",
    )
    days_ahead: int = Field(default=1, ge=1, le=30)


# ============================================================ #
# Responses
# ============================================================ #
class PredictionItem(BaseModel):
    day: int = Field(..., description="Posição no horizonte de previsão (1, 2, ...).")
    predicted_price: float


class PredictResponse(BaseModel):
    predictions: List[PredictionItem]
    inference_time_ms: float


class SymbolPredictResponse(BaseModel):
    symbol: str
    last_close: float
    last_close_date: str
    predictions: List[PredictionItem]
    inference_time_ms: float


class HealthResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    status: str
    model_loaded: bool
    version: str


class ModelInfoResponse(BaseModel):
    symbol_trained_on: str
    window_size: int
    lstm_units_1: int
    lstm_units_2: int
    dropout_rate: float
    epochs_trained: int
    train_samples: int
    test_samples: int
    metrics: dict
    trained_at: str


class ErrorResponse(BaseModel):
    detail: str
    error_type: Optional[str] = None
