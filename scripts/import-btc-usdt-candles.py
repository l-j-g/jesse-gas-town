#!/usr/bin/env python
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from jesse import research
from jesse.enums import exchanges


def main() -> None:
    parser = argparse.ArgumentParser(description='Import public BTC-USDT 1m candles through Jesse.')
    parser.add_argument('--exchange', default=exchanges.BYBIT_USDT_PERPETUAL)
    parser.add_argument('--symbol', default='BTC-USDT')
    parser.add_argument('--start', required=True, help='YYYY-MM-DD, must be before today')
    args = parser.parse_args()

    print(research.import_candles(args.exchange, args.symbol, args.start, show_progressbar=False))


if __name__ == '__main__':
    main()
