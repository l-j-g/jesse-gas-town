#!/usr/bin/env python
import argparse
import json
import os
import sys
from pathlib import Path

import arrow

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

import jesse.helpers as jh
from jesse import research
from jesse.enums import exchanges
from strategies.BaselineMaTrend import BaselineMaTrend


def main() -> None:
    parser = argparse.ArgumentParser(description='Run BaselineMaTrend on imported Jesse DB candles.')
    parser.add_argument('--exchange', default=exchanges.BINANCE_PERPETUAL_FUTURES)
    parser.add_argument('--symbol', default='BTC-USDT')
    parser.add_argument('--start', default='2024-01-01')
    parser.add_argument('--finish', default='2024-06-01')
    parser.add_argument('--fee', type=float, default=0.0004)
    parser.add_argument('--leverage', type=int, default=1)
    args = parser.parse_args()

    start_ts = jh.arrow_to_timestamp(arrow.get(args.start, 'YYYY-MM-DD'))
    finish_ts = jh.arrow_to_timestamp(arrow.get(args.finish, 'YYYY-MM-DD'))
    warmup, candles = research.get_candles(
        args.exchange,
        args.symbol,
        '1m',
        start_ts,
        finish_ts,
        warmup_candles_num=0,
        is_for_jesse=True,
    )

    config = {
        'starting_balance': 10_000,
        'fee': args.fee,
        'type': 'futures',
        'futures_leverage': args.leverage,
        'futures_leverage_mode': 'cross',
        'exchange': args.exchange,
        'warm_up_candles': 0,
    }
    routes = [
        {
            'exchange': args.exchange,
            'strategy': BaselineMaTrend,
            'symbol': args.symbol,
            'timeframe': '1h',
        },
    ]
    candle_map = {
        jh.key(args.exchange, args.symbol): {
            'exchange': args.exchange,
            'symbol': args.symbol,
            'candles': candles,
        },
    }
    warmup_map = None
    if warmup is not None:
        warmup_map = {
            jh.key(args.exchange, args.symbol): {
                'exchange': args.exchange,
                'symbol': args.symbol,
                'candles': warmup,
            },
        }

    result = research.backtest(
        config,
        routes,
        [],
        candle_map,
        warmup_candles=warmup_map,
        generate_equity_curve=True,
        generate_logs=False,
        fast_mode=True,
    )

    print(json.dumps(result['metrics'], indent=2, sort_keys=True, default=str))


if __name__ == '__main__':
    main()
