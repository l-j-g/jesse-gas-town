import numpy as np

import jesse.helpers as jh
from jesse.config import config, reset_config
from jesse.enums import exchanges
from jesse.modes import backtest_mode
from jesse.store import store


def _build_candles(first_open: float, closes: list[float]) -> np.ndarray:
    timestamp = 1609459200000
    prev_close = first_open
    candles = []

    for close_price in closes:
        open_price = prev_close
        high_price = max(open_price, close_price)
        low_price = min(open_price, close_price)
        candles.append([timestamp, open_price, close_price, high_price, low_price, 1])
        prev_close = close_price
        timestamp += 60_000

    return np.array(candles, dtype=np.float64)


def _run_backtest(candles: np.ndarray):
    reset_config()
    config['env']['exchanges'][exchanges.SANDBOX]['type'] = 'futures'
    config['env']['exchanges'][exchanges.SANDBOX]['balance'] = 10_000

    routes = [
        {'symbol': 'BTC-USDT', 'timeframe': '1m', 'strategy': 'RangeBarBreakoutPullbackScalp'}
    ]

    candle_map = {
        jh.key(exchanges.SANDBOX, 'BTC-USDT'): {
            'exchange': exchanges.SANDBOX,
            'symbol': 'BTC-USDT',
            'candles': candles
        }
    }

    backtest_mode.run('000', False, {}, exchanges.SANDBOX, routes, [], '2019-04-01', '2019-04-02', candle_map)


def test_range_bar_breakout_pullback_scalp_long_trade():
    candles = _build_candles(
        10,
        [11, 12, 13, 14, 15, 16, 15, 14, 15, 16, 17, 18, 17, 16, 15, 14]
    )

    _run_backtest(candles)

    assert len(store.closed_trades.trades) == 1
    trade = store.closed_trades.trades[0]

    assert trade.type == 'long'
    assert trade.entry_price == 16
    assert trade.exit_price == 17
    assert len(trade.orders) == 3


def test_range_bar_breakout_pullback_scalp_short_trade():
    candles = _build_candles(
        20,
        [19, 18, 17, 16, 15, 14, 15, 16, 15, 14, 13, 12, 13, 14, 15, 16]
    )

    _run_backtest(candles)

    assert len(store.closed_trades.trades) == 1
    trade = store.closed_trades.trades[0]

    assert trade.type == 'short'
    assert trade.entry_price == 14
    assert trade.exit_price == 13
    assert len(trade.orders) == 3


def test_range_bar_breakout_pullback_scalp_requires_pullback():
    candles = _build_candles(
        10,
        [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    )

    _run_backtest(candles)

    assert len(store.closed_trades.trades) == 0
