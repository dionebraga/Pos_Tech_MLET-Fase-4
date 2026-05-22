"""
src/data_loader.py
------------------
Carrega dados históricos de ações usando yfinance 1.x.

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
    """Baixa dados históricos de uma ação via yfinance 1.x.

    yfinance >= 1.0 gerencia autenticação/cookies internamente.
    Passar curl_cffi.Session causa incompatibilidade — não é mais necessário.
    """
    logger.info("Baixando dados de %s [%s a %s, interval=%s]", symbol, start, end, interval)

    ticker = yf.Ticker(symbol)
    df = ticker.history(start=start, end=end, interval=interval)

    if df.empty:
        raise ValueError(
            f"Nenhum dado retornado para o símbolo '{symbol}'. "
            f"Verifique o ticker e o intervalo de datas ({start} a {end})."
        )

    df = df.reset_index()

    # Normaliza coluna de data (remove timezone se houver)
    date_col = "Date" if "Date" in df.columns else df.columns[0]
    if pd.api.types.is_datetime64tz_dtype(df[date_col]):
        df[date_col] = df[date_col].dt.tz_convert(None)

    logger.info("OK — %d registros baixados para %s", len(df), symbol)
    return df


def fetch_recent_window(symbol: str, window_size: int = 60) -> pd.Series:
    """Busca os últimos `window_size` preços de fechamento para previsão.

    Args:
        symbol: Ticker da ação (ex: AAPL, PETR4.SA).
        window_size: Quantidade de preços de fechamento necessários.

    Returns:
        pd.Series com window_size preços de fechamento (mais antigo → recente).
    """
    end = pd.Timestamp.now()
    start = end - pd.DateOffset(days=window_size * 2)  # folga para fins de semana/feriados

    logger.info("Buscando janela recente para %s (%d dias)", symbol, window_size)
    ticker = yf.Ticker(symbol)
    df = ticker.history(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))

    if df.empty:
        raise ValueError(
            f"Nenhum dado retornado para '{symbol}'. "
            "Verifique o ticker e conectividade."
        )

    closes = df["Close"]
    if len(closes) < window_size:
        raise ValueError(
            f"Apenas {len(closes)} registros disponíveis para '{symbol}', "
            f"mas são necessários {window_size}. Tente um ticker com mais dados."
        )

    return closes.iloc[-window_size:]


def get_close_prices(df: pd.DataFrame) -> pd.Series:
    """Extrai a coluna 'Close' do DataFrame, suportando colunas MultiIndex (yfinance 1.x)."""
    close = df["Close"]
    # yf.download() retorna MultiIndex quando há múltiplos tickers; converte para Series
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    return close.dropna()


def save_raw_data(df: pd.DataFrame, path: str) -> None:
    df.to_csv(path, index=False)
    logger.info("Dados salvos em: %s", path)


def load_raw_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["Date"])
    logger.info("Dados carregados de: %s (%d registros)", path, len(df))
    return df


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    df = fetch_stock_data("AAPL", "2024-01-01", "2024-07-01")
    print(df.head())
    print(f"\nTotal de registros: {len(df)}")
