#!/usr/bin/env python
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

import jesse.helpers as jh
from jesse import research
from jesse.enums import exchanges
from strategies.BaselineMaTrend import BaselineMaTrend


def synthetic_btc_1m_candles(days: int = 90) -> np.ndarray:
    """Deterministic synthetic 1m candles with reversals after MA warmup."""
    candles = []
    timestamp = 1704067200000
    price = 42_000.0
    total_minutes = days * 24 * 60

    for i in range(total_minutes):
        regime = i / total_minutes
        if regime < 0.30:
            drift = -0.18
        elif regime < 0.62:
            drift = 0.52
        elif regime < 0.75:
            drift = 0.01
        else:
            drift = -0.48

        wave = math.sin(i / 240) * 7.5 + math.sin(i / 37) * 2.0
        open_price = price
        close_price = max(100.0, price + drift + wave * 0.03)
        high_price = max(open_price, close_price) + 12.0
        low_price = min(open_price, close_price) - 12.0
        volume = 100.0 + abs(wave) * 3.0
        candles.append([timestamp, open_price, close_price, high_price, low_price, volume])
        price = close_price
        timestamp += 60_000

    return np.array(candles, dtype=np.float64)


def main() -> None:
    exchange = exchanges.SANDBOX
    symbol = 'BTC-USDT'
    config = {
        'starting_balance': 10_000,
        'fee': 0.0004,
        'type': 'futures',
        'futures_leverage': 1,
        'futures_leverage_mode': 'cross',
        'exchange': exchange,
        'warm_up_candles': 0,
    }
    routes = [
        {
            'exchange': exchange,
            'strategy': BaselineMaTrend,
            'symbol': symbol,
            'timeframe': '1h',
        },
    ]
    candles = {
        jh.key(exchange, symbol): {
            'exchange': exchange,
            'symbol': symbol,
            'candles': synthetic_btc_1m_candles(),
        },
    }

    result = research.backtest(
        config,
        routes,
        [],
        candles,
        generate_equity_curve=True,
        generate_logs=False,
        fast_mode=True,
    )

    print(json.dumps(result['metrics'], indent=2, sort_keys=True, default=str))


if __name__ == '__main__':
    main()
