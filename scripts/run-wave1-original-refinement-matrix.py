#!/usr/bin/env python
import argparse
import csv
import importlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import arrow

ROOT = Path(__file__).resolve().parents[1]
PREP_SCRIPT = ROOT / 'scripts' / 'prepare-wave1-private-strategies.py'
RUNTIME_ROOT = ROOT / '.runtime' / 'wave1-private-strategies'
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

import jesse.helpers as jh
from jesse import research
from jesse.enums import exchanges


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
    'open_pl',
    'fee',
]

DEFAULT_PAIRS = [
    ('KAMA_TrendFollowing', 'KamaPullbackReclaim', '15m'),
    ('SuperScalper', 'SuperScalperTimeStopScratch', '15m'),
    ('TrendWaveRiderV2', 'TrendWaveRiderV2ShallowPullbackBand', '15m'),
    ('TurtleV2', 'TurtleV2FailedBreakTimeStop', '1h'),
]

DEFAULT_DATA_TIMEFRAMES = ('4h', '6h')


def parse_csv_values(value: str, cast):
    return [cast(v.strip()) for v in value.split(',') if v.strip()]


def timestamp(date_value: str) -> int:
    return jh.arrow_to_timestamp(arrow.get(date_value, 'YYYY-MM-DD'))


def load_prepare_module():
    spec = importlib.util.spec_from_file_location('prepare_wave1_private_strategies', PREP_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare_runtime(runtime_root: Path = RUNTIME_ROOT) -> dict:
    prep = load_prepare_module()
    source_root = prep.DEFAULT_SOURCE_ROOT.resolve()
    runtime_root = runtime_root.resolve()
    runtime_root.mkdir(parents=True, exist_ok=True)
    prep.write_package_init(runtime_root)

    originals = [prep.prepare_strategy(source_root, runtime_root, s) for s in prep.WAVE1_ORIGINALS]
    prepared_originals = {row['class_name'] for row in originals if row.get('prepared')}
    refinements = [
        prep.prepare_refinement(runtime_root, refinement, prepared_originals)
        for refinement in prep.REFINEMENT_QUEUE
    ]
    prep.check_imports(runtime_root, originals)
    prep.check_imports(runtime_root, refinements)

    manifest = {
        'runtime_root': str(runtime_root),
        'originals': originals,
        'refinements': refinements,
    }
    (runtime_root / 'manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    return manifest


def strategy_class(runtime_root: Path, class_name: str):
    runtime_root = runtime_root.resolve()
    if str(runtime_root) not in sys.path:
        sys.path.insert(0, str(runtime_root))
    module = importlib.import_module(f'strategies.{class_name}')
    return getattr(module, class_name)


def profit_factor(metrics: dict) -> float | None:
    gross_loss = metrics.get('gross_loss') or 0
    if gross_loss == 0:
        return None
    return abs((metrics.get('gross_profit') or 0) / gross_loss)


def decision(metrics: dict) -> str:
    total = metrics.get('total') or 0
    expectancy = metrics.get('expectancy') or 0
    net_pct = metrics.get('net_profit_percentage') or 0
    max_drawdown = metrics.get('max_drawdown') or 0

    if total < 10:
        return 'reject: too few trades'
    if expectancy <= 0 or net_pct <= 0:
        return 'reject: non-positive expectancy after fees'
    if max_drawdown < -20:
        return 'revise: positive but drawdown too high'
    return 'revise: positive slice, needs route robustness'


def run_case(
    runtime_root: Path,
    exchange: str,
    symbol: str,
    strategy_name: str,
    timeframe: str,
    start: str,
    finish: str,
    fee: float,
    leverage: int,
) -> dict:
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
        'futures_leverage': leverage,
        'futures_leverage_mode': 'cross',
        'exchange': exchange,
        'warm_up_candles': 0,
    }
    routes = [
        {
            'exchange': exchange,
            'strategy': strategy_class(runtime_root, strategy_name),
            'symbol': symbol,
            'timeframe': timeframe,
        },
    ]
    data_routes = [
        {
            'exchange': exchange,
            'symbol': symbol,
            'timeframe': data_timeframe,
        }
        for data_timeframe in DEFAULT_DATA_TIMEFRAMES
        if data_timeframe != timeframe
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
        data_routes,
        candle_map,
        generate_equity_curve=False,
        generate_logs=False,
        fast_mode=True,
    )
    metrics = result['metrics']
    row = {
        'exchange': exchange,
        'symbol': symbol,
        'timeframe': timeframe,
        'strategy': strategy_name,
        'start': start,
        'finish': finish,
        'fee_rate': fee,
        'leverage': leverage,
        'status': 'ok',
        'error': '',
    }
    for key in METRIC_KEYS:
        row[key] = metrics.get(key)
    row['profit_factor'] = profit_factor(metrics)
    row['decision'] = decision(metrics)
    return row


def error_row(exchange: str, symbol: str, strategy_name: str, timeframe: str, start: str, finish: str, fee: float, leverage: int, exc: Exception) -> dict:
    row = {
        'exchange': exchange,
        'symbol': symbol,
        'timeframe': timeframe,
        'strategy': strategy_name,
        'start': start,
        'finish': finish,
        'fee_rate': fee,
        'leverage': leverage,
        'status': 'error',
        'error': f'{type(exc).__name__}: {exc}',
        'profit_factor': None,
        'decision': 'blocked: runtime error',
    }
    for key in METRIC_KEYS:
        row[key] = None
    return row


def process_error_row(
    exchange: str,
    symbol: str,
    strategy_name: str,
    timeframe: str,
    start: str,
    finish: str,
    fee: float,
    leverage: int,
    returncode: int,
    stderr: str,
) -> dict:
    lines = [line.strip() for line in stderr.splitlines() if line.strip()]
    summary = next((line for line in reversed(lines) if not line.startswith('Extension modules:')), '')
    if any('Fatal Python error' in line for line in lines):
        summary = next(line for line in lines if 'Fatal Python error' in line)
    row = error_row(
        exchange,
        symbol,
        strategy_name,
        timeframe,
        start,
        finish,
        fee,
        leverage,
        RuntimeError(f'child process failed with returncode {returncode}'),
    )
    row['error'] = f'child process failed with returncode {returncode}: {summary}'
    return row


def run_case_subprocess(args: argparse.Namespace, strategy_name: str, symbol: str, timeframe: str) -> dict:
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        '--child-case',
        '--exchange',
        args.exchange,
        '--symbols',
        symbol,
        '--start',
        args.start,
        '--finish',
        args.finish,
        '--fee',
        str(args.fee),
        '--leverage',
        str(args.leverage),
        '--runtime-root',
        str(args.runtime_root),
        '--child-strategy',
        strategy_name,
        '--child-timeframe',
        timeframe,
    ]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        return process_error_row(
            args.exchange,
            symbol,
            strategy_name,
            timeframe,
            args.start,
            args.finish,
            args.fee,
            args.leverage,
            result.returncode,
            result.stderr,
        )
    for line in reversed(result.stdout.splitlines()):
        if line.startswith('{'):
            return json.loads(line)
    return process_error_row(
        args.exchange,
        symbol,
        strategy_name,
        timeframe,
        args.start,
        args.finish,
        args.fee,
        args.leverage,
        result.returncode,
        'child produced no JSON row',
    )


def comparison_rows(rows: list[dict], pairs: list[tuple[str, str, str]]) -> list[dict]:
    indexed = {(r['strategy'], r['symbol'], r['timeframe']): r for r in rows if r['status'] == 'ok'}
    comparisons = []
    for original, refinement, timeframe in pairs:
        symbols = sorted({r['symbol'] for r in rows if r['timeframe'] == timeframe})
        for symbol in symbols:
            base = indexed.get((original, symbol, timeframe))
            variant = indexed.get((refinement, symbol, timeframe))
            if not base or not variant:
                continue
            comparisons.append({
                'symbol': symbol,
                'timeframe': timeframe,
                'original': original,
                'refinement': refinement,
                'net_profit_percentage_delta': (variant.get('net_profit_percentage') or 0) - (base.get('net_profit_percentage') or 0),
                'expectancy_delta': (variant.get('expectancy') or 0) - (base.get('expectancy') or 0),
                'max_drawdown_delta': (variant.get('max_drawdown') or 0) - (base.get('max_drawdown') or 0),
                'trade_count_delta': (variant.get('total') or 0) - (base.get('total') or 0),
                'original_decision': base.get('decision'),
                'refinement_decision': variant.get('decision'),
            })
    return comparisons


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description='Run Wave 1 original-vs-refinement local backtests.')
    parser.add_argument('--exchange', default=exchanges.BINANCE_PERPETUAL_FUTURES)
    parser.add_argument('--symbols', default='BTC-USDT')
    parser.add_argument('--start', default='2024-01-01')
    parser.add_argument('--finish', default='2024-02-01')
    parser.add_argument('--fee', type=float, default=0.0004)
    parser.add_argument('--leverage', type=int, default=3)
    parser.add_argument('--runtime-root', type=Path, default=RUNTIME_ROOT)
    parser.add_argument('--csv', default='docs/backtests/2026-06-02-wave1-original-refinement-smoke.csv')
    parser.add_argument('--json', default='docs/backtests/2026-06-02-wave1-original-refinement-smoke.json')
    parser.add_argument('--child-case', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--child-strategy', default='', help=argparse.SUPPRESS)
    parser.add_argument('--child-timeframe', default='', help=argparse.SUPPRESS)
    args = parser.parse_args()

    runtime_root = args.runtime_root.resolve()
    manifest = prepare_runtime(runtime_root)
    if not all(r.get('prepared') for r in manifest['originals'] + manifest['refinements']):
        raise SystemExit('not all Wave 1 originals/refinements prepared')

    if args.child_case:
        symbol = parse_csv_values(args.symbols, str)[0]
        row = run_case(
            runtime_root,
            args.exchange,
            symbol,
            args.child_strategy,
            args.child_timeframe,
            args.start,
            args.finish,
            args.fee,
            args.leverage,
        )
        print(json.dumps(row, sort_keys=True, default=str))
        return

    symbols = parse_csv_values(args.symbols, str)
    rows = []
    for original, refinement, timeframe in DEFAULT_PAIRS:
        for strategy_name in (original, refinement):
            for symbol in symbols:
                row = run_case_subprocess(args, strategy_name, symbol, timeframe)
                rows.append(row)
                print(json.dumps(row, sort_keys=True, default=str))

    comparisons = comparison_rows(rows, DEFAULT_PAIRS)
    csv_path = ROOT / args.csv
    json_path = ROOT / args.json
    write_csv(csv_path, rows)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps({'rows': rows, 'comparisons': comparisons}, indent=2, sort_keys=True, default=str) + '\n')


if __name__ == '__main__':
    main()
