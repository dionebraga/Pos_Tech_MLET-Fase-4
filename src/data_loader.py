"""
src/data_loader.py
------------------
Carrega dados históricos de ações usando yfinance + curl_cffi.

Construído por: Dione Braga Ferreira
Tech Challenge Fase 4 — PósTech MLET FIAP
"""

import logging

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


def fetch_stock_data(
    symbol: str,
    start: str,
    end: str,
    interval: str = "1d",
) -> pd.DataFrame:
    """Baixa dados históricos de uma ação via yfinance.

    Usa curl_cffi para contornar o bloqueio do Yahoo Finance (necessário no
    yfinance >= 0.2.50, que exige session do curl_cffi e não mais requests).
    """
    try:
        from curl_cffi import requests as cffi_requests
    except ImportError as exc:
        raise ImportError(
            "curl_cffi é obrigatório para o yfinance funcionar. "
            "Instale com: pip install curl_cffi"
        ) from exc

    logger.info(f"Baixando dados de {symbol} [{start} a {end}, interval={interval}]")

    session = cffi_requests.Session(impersonate="chrome")
    ticker = yf.Ticker(symbol, session=session)

    df = ticker.history(
        start=start, end=end, interval=interval, auto_adjust=False,
    )

    if df.empty:
        raise ValueError(
            f"Nenhum dado retornado para o símbolo '{symbol}'. "
            f"Verifique o ticker e o intervalo de datas ({start} a {end})."
        )

    df = df.reset_index()
    if isinstance(df["Date"].dtype, pd.DatetimeTZDtype):
        df["Date"] = df["Date"].dt.tz_localize(None)

    logger.info(f"OK — {len(df)} registros baixados para {symbol}")
    return df


def fetch_recent_window(symbol: str, window_size: int = 60) -> pd.Series:
    """Busca os últimos `window_size` + 30 dias de fechamento para previsão.

    Args:
        symbol: Ticker da ação (ex: AAPL, PETR4.SA).
        window_size: Quantidade de preços de fechamento necessários.

    Returns:
        pd.Series com window_size preços de fechamento (mais antigo → recente).
    """
    try:
        from curl_cffi import requests as cffi_requests
    except ImportError as exc:
        raise ImportError("curl_cffi é obrigatório.") from exc

    end = pd.Timestamp.now()
    start = end - pd.DateOffset(days=window_size * 2)  # folga para dias úteis

    logger.info("Buscando janela recente para %s (%d dias)", symbol, window_size)
    session = cffi_requests.Session(impersonate="chrome")
    ticker = yf.Ticker(symbol, session=session)
    df = ticker.history(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))

    if df.empty:
        raise ValueError(
            f"Nenhum dado retornado para '{symbol}'. "
            f"Verifique o ticker e conectividade."
        )

    closes = df["Close"]
    if len(closes) < window_size:
        raise ValueError(
            f"Apenas {len(closes)} registros disponíveis para '{symbol}', "
            f"mas são necessários {window_size}. Tente um ticker com mais dados."
        )

    return closes.iloc[-window_size:]


def get_close_prices(df: pd.DataFrame) -> pd.Series:
    """Extrai a coluna 'Close' do DataFrame baixado."""
    return df["Close"]


def save_raw_data(df: pd.DataFrame, path: str) -> None:
    df.to_csv(path, index=False)
    logger.info(f"Dados salvos em: {path}")


def load_raw_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["Date"])
    logger.info(f"Dados carregados de: {path} ({len(df)} registros)")
    return df


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    df = fetch_stock_data("AAPL", "2024-01-01", "2024-07-01")
    print(df.head())
    print(f"\nTotal de registros: {len(df)}")
