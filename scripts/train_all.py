"""
Treina modelos LSTM para múltiplos tickers em sequência.

Uso:
    python scripts/train_all.py
    python scripts/train_all.py --symbols AAPL MSFT TSLA
    python scripts/train_all.py --symbols PETR4.SA VALE3.SA --epochs 30
"""
import argparse
import subprocess
import sys

SYMBOLS_DEFAULT = [
    "AAPL", "MSFT", "GOOGL", "AMZN",
    "TSLA", "META", "NVDA",
    "PETR4.SA", "VALE3.SA", "ITUB4.SA",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Treina LSTM para múltiplos tickers.")
    parser.add_argument(
        "--symbols", nargs="+", default=SYMBOLS_DEFAULT,
        metavar="TICKER",
        help=f"Tickers a treinar (default: {len(SYMBOLS_DEFAULT)} ativos)",
    )
    parser.add_argument("--epochs", type=int, default=50, help="Épocas por ticker")
    args = parser.parse_args()

    total = len(args.symbols)
    failed = []

    for i, symbol in enumerate(args.symbols, 1):
        print(f"\n{'='*60}")
        print(f"  [{i}/{total}] Treinando {symbol}")
        print(f"{'='*60}")
        result = subprocess.run(
            [
                sys.executable, "-m", "src.train",
                "--symbol", symbol,
                "--epochs", str(args.epochs),
            ],
            check=False,
        )
        if result.returncode != 0:
            print(f"  ⚠  Falhou para {symbol} — continuando...")
            failed.append(symbol)

    print(f"\n{'='*60}")
    if failed:
        print(f"  ✅ Concluído com erros em: {', '.join(failed)}")
    else:
        print(f"  ✅ Todos os {total} modelos treinados com sucesso.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
