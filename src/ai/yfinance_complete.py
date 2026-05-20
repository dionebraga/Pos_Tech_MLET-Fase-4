import yfinance as yf
import pandas as pd

def download_stock_data(
    symbol="AAPL",
    period="2y",
    interval="1d"
):

    df = yf.download(
        tickers=symbol,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False,
        threads=False
    )

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.dropna(inplace=True)

    return df

def get_company_info(symbol="AAPL"):

    ticker = yf.Ticker(symbol)

    return ticker.info

def get_news(symbol="AAPL"):

    ticker = yf.Ticker(symbol)

    return ticker.news

def get_balance_sheet(symbol="AAPL"):

    ticker = yf.Ticker(symbol)

    return ticker.balance_sheet

def get_cashflow(symbol="AAPL"):

    ticker = yf.Ticker(symbol)

    return ticker.cashflow

def get_recommendations(symbol="AAPL"):

    ticker = yf.Ticker(symbol)

    return ticker.recommendations

def get_earnings(symbol="AAPL"):

    ticker = yf.Ticker(symbol)

    return ticker.earnings