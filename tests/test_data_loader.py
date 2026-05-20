"""Testes do data_loader (sem hit em rede real)."""
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.data_loader import fetch_stock_data, get_close_prices


@pytest.fixture
def mock_yfinance():
    """Mocka o yfinance + curl_cffi session usados pelo data_loader."""
    with patch("src.data_loader.yf.Ticker") as mock_ticker, \
         patch("curl_cffi.requests.Session") as mock_session:

        mock_session.return_value = MagicMock()
        ticker_instance = MagicMock()
        mock_ticker.return_value = ticker_instance
        yield ticker_instance


def test_fetch_stock_data_returns_dataframe(mock_yfinance):
    # yfinance retorna DataFrame com DatetimeIndex nomeado "Date"
    idx = pd.date_range("2024-01-01", periods=3, tz="America/New_York", name="Date")
    mock_df = pd.DataFrame({
        "Open": [100, 101, 102],
        "High": [105, 106, 107],
        "Low": [99, 100, 101],
        "Close": [104, 105, 106],
        "Volume": [1000, 2000, 3000],
    }, index=idx)
    mock_yfinance.history.return_value = mock_df

    result = fetch_stock_data("AAPL", "2024-01-01", "2024-01-04")
    assert len(result) == 3
    assert "Close" in result.columns
    # reset_index() converte o index em coluna Date
    assert "Date" in result.columns


def test_fetch_stock_data_raises_on_empty(mock_yfinance):
    mock_yfinance.history.return_value = pd.DataFrame()
    with pytest.raises(ValueError, match="Nenhum dado"):
        fetch_stock_data("INVALID", "2024-01-01", "2024-01-04")


def test_get_close_prices():
    df = pd.DataFrame({"Close": [100.0, 101.0, 102.0]})
    closes = get_close_prices(df)
    assert len(closes) == 3
    assert closes.iloc[0] == 100.0
