"""
Configuração centralizada da aplicação usando Pydantic Settings.

Lê variáveis de ambiente de um arquivo .env (se existir) e fornece
valores default seguros para todos os hiperparâmetros.
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Configurações globais lidas de variáveis de ambiente."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---------- Dados ----------
    DEFAULT_SYMBOL: str = "AAPL"
    DEFAULT_START_DATE: str = "2018-01-01"
    DEFAULT_END_DATE: str = "2024-07-20"

    # ---------- Modelo ----------
    WINDOW_SIZE: int = 60          # qtd de dias usados para prever o próximo
    LSTM_UNITS_1: int = 64
    LSTM_UNITS_2: int = 64
    DROPOUT_RATE: float = 0.2
    EPOCHS: int = 50
    BATCH_SIZE: int = 32
    LEARNING_RATE: float = 0.001
    TRAIN_SPLIT: float = 0.8       # 80% treino, 20% teste

    # ---------- Caminhos ----------
    MODEL_PATH: str = str(PROJECT_ROOT / "models" / "lstm_model.keras")
    SCALER_PATH: str = str(PROJECT_ROOT / "models" / "scaler.pkl")
    METADATA_PATH: str = str(PROJECT_ROOT / "models" / "metadata.json")

    # ---------- API ----------
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    LOG_LEVEL: str = "INFO"


# Instância singleton de configurações
settings = Settings()
