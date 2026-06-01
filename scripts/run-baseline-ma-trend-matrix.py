#!/usr/bin/env python
import argparse
import csv
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


DEFAULT_SLICES = [
    ('uptrend', '2023-10-01', '2024-03-15'),
    ('choppy', '2024-03-15', '2024-06-15'),
    ('downtrend', '2024-06-15', '2024-09-15'),
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
    'longs_count',
    'shorts_count',
    'total_open_trades',
    'open_pl',
    'fee',
]


def parse_csv_values(value: str, cast):
    return [cast(v.strip()) for v in value.split(',') if v.strip()]


def timestamp(date_value: str) -> int:
    return jh.arrow_to_timestamp(arrow.get(date_value, 'YYYY-MM-DD'))


def run_case(exchange: str, symbol: str, regime: str, start: str, finish: str, fee: float, slippage_bps: float) -> dict:
    effective_fee = fee + (slippage_bps / 10_000)
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
        'fee': effective_fee,
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
        'timeframe': '1h',
        'regime': regime,
        'start': start,
        'finish': finish,
        'base_fee': fee,
        'slippage_bps': slippage_bps,
        'effective_fee': effective_fee,
    }
    for key in METRIC_KEYS:
        row[key] = metrics.get(key)
    row['decision'] = decision(metrics)
    return row


def decision(metrics: dict) -> str:
    total = metrics.get('total') or 0
    net_pct = metrics.get('net_profit_percentage') or 0
    max_drawdown = metrics.get('max_drawdown') or 0
    sharpe = metrics.get('sharpe_ratio') or 0

    if total < 10:
        return 'reject: too few trades'
    if net_pct <= 0:
        return 'reject: negative/flat net'
    if max_drawdown < -0.10:
        return 'reject: drawdown too high'
    if sharpe < 0.5:
        return 'revise: weak risk-adjusted return'
    return 'keep as baseline control'


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description='Run BaselineMaTrend route/regime/cost matrix.')
    parser.add_argument('--exchange', default=exchanges.BINANCE_PERPETUAL_FUTURES)
    parser.add_argument('--symbols', default='BTC-USDT,ETH-USDT')
    parser.add_argument('--fees', default='0.0004,0.0008')
    parser.add_argument('--slippage-bps', default='0,2')
    parser.add_argument('--csv', default='docs/backtests/2026-06-02-baseline-ma-trend-matrix.csv')
    parser.add_argument('--json', default='')
    args = parser.parse_args()

    rows = []
    symbols = parse_csv_values(args.symbols, str)
    fees = parse_csv_values(args.fees, float)
    slippage_values = parse_csv_values(args.slippage_bps, float)

    for symbol in symbols:
        for regime, start, finish in DEFAULT_SLICES:
            for fee in fees:
                for slippage_bps in slippage_values:
                    row = run_case(args.exchange, symbol, regime, start, finish, fee, slippage_bps)
                    rows.append(row)
                    print(json.dumps(row, sort_keys=True, default=str))

    csv_path = ROOT / args.csv
    write_csv(csv_path, rows)

    if args.json:
        json_path = ROOT / args.json
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(rows, indent=2, sort_keys=True, default=str) + '\n')


if __name__ == '__main__':
    main()
