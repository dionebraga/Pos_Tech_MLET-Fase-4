import yfinance as yf
import pandas as pd

df = yf.download("AAPL", start="2018-01-01", end="2026-05-01", progress=False)
df = df.reset_index()
df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
df.to_csv("data/AAPL_2018_2026.csv", index=False)
print(f"Salvo: data/AAPL_2018_2026.csv — {len(df)} linhas")
print(f"Inicio: {df['Date'].min().date()}  |  Fim: {df['Date'].max().date()}")
