import importlib.util
from pathlib import Path

import jesse.helpers as jh
from jesse import research
from jesse.enums import exchanges


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / 'scripts' / 'run-baseline-ma-trend-backtest.py'
spec = importlib.util.spec_from_file_location('baseline_backtest_runner', SCRIPT_PATH)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def test_baseline_ma_trend_research_backtest_runs():
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
            'strategy': runner.BaselineMaTrend,
            'symbol': symbol,
            'timeframe': '1h',
        },
    ]
    candles = {
        jh.key(exchange, symbol): {
            'exchange': exchange,
            'symbol': symbol,
            'candles': runner.synthetic_btc_1m_candles(days=45),
        },
    }

    result = research.backtest(config, routes, [], candles, fast_mode=True)

    assert 'metrics' in result
    assert {'total', 'win_rate', 'net_profit_percentage'} <= set(result['metrics'])
    assert result['metrics']['total'] > 0
