#!/usr/bin/env python
import argparse
import csv
import importlib
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


DEFAULT_STRATEGIES = [
    'RangeBarBreakoutPullbackScalp',
    'RangeBarBollingerMeanReversion',
]

METRIC_KEYS = [
    'net_profit',
    'net_profit_percentage',
    'annual_return',
    'max_drawdown',
    'sharpe_ratio',
    'sortino_ratio',
    'calmar_ratio',
    'win_rate',
    'total',
    'expectancy',
    'gross_profit',
    'gross_loss',
    'longs_count',
    'shorts_count',
    'total_open_trades',
    'fee',
]


def parse_csv_values(value: str, cast):
    return [cast(v.strip()) for v in value.split(',') if v.strip()]


def timestamp(date_value: str) -> int:
    return jh.arrow_to_timestamp(arrow.get(date_value, 'YYYY-MM-DD'))


def strategy_class(name: str):
    module = importlib.import_module(f'jesse.strategies.{name}')
    return getattr(module, name)


def profit_factor(metrics: dict) -> float | None:
    gross_loss = metrics.get('gross_loss') or 0
    if gross_loss == 0:
        return None
    return abs((metrics.get('gross_profit') or 0) / gross_loss)


def decision(metrics: dict) -> str:
    total = metrics.get('total') or 0
    expectancy = metrics.get('expectancy') or 0
    net_pct = metrics.get('net_profit_percentage') or 0

    if total < 10:
        return 'reject: too few trades'
    if expectancy <= 0 or net_pct <= 0:
        return 'reject: non-positive expectancy after fees'
    return 'revise: positive slice, needs route robustness'


def run_case(exchange: str, symbol: str, strategy_name: str, start: str, finish: str, fee: float) -> dict:
    _, candles = research.get_candles(
        exchange,
        symbol,
        '1m',
        timestamp(start),
        timestamp(finish),
        warmup_candles_num=0,
        is_for_jesse=True,
    )

    config = {
        'starting_balance': 10_000,
        'fee': fee,
        'type': 'futures',
        'futures_leverage': 1,
        'futures_leverage_mode': 'cross',
        'exchange': exchange,
        'warm_up_candles': 0,
    }
    routes = [
        {
            'exchange': exchange,
            'strategy': strategy_class(strategy_name),
            'symbol': symbol,
            'timeframe': '1m',
        },
    ]
    candle_map = {
        jh.key(exchange, symbol): {
            'exchange': exchange,
            'symbol': symbol,
            'candles': candles,
        },
    }

    result = research.backtest(
        config,
        routes,
        [],
        candle_map,
        generate_equity_curve=False,
        generate_logs=False,
        fast_mode=True,
    )
    metrics = result['metrics']
    row = {
        'exchange': exchange,
        'symbol': symbol,
        'timeframe': '1m',
        'strategy': strategy_name,
        'start': start,
        'finish': finish,
        'fee_rate': fee,
    }
    for key in METRIC_KEYS:
        row[key] = metrics.get(key)
    row['profit_factor'] = profit_factor(metrics)
    row['decision'] = decision(metrics)
    return row


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description='Run executable range-bar candidate backtests.')
    parser.add_argument('--exchange', default=exchanges.BINANCE_PERPETUAL_FUTURES)
    parser.add_argument('--symbols', default='BTC-USDT,ETH-USDT')
    parser.add_argument('--strategies', default=','.join(DEFAULT_STRATEGIES))
    parser.add_argument('--start', default='2024-01-01')
    parser.add_argument('--finish', default='2024-06-01')
    parser.add_argument('--fee', type=float, default=0.0004)
    parser.add_argument('--csv', default='docs/backtests/2026-06-02-range-bar-candidates.csv')
    args = parser.parse_args()

    rows = []
    for strategy_name in parse_csv_values(args.strategies, str):
        for symbol in parse_csv_values(args.symbols, str):
            row = run_case(args.exchange, symbol, strategy_name, args.start, args.finish, args.fee)
            rows.append(row)
            print(json.dumps(row, sort_keys=True, default=str))

    write_csv(ROOT / args.csv, rows)


if __name__ == '__main__':
    main()
