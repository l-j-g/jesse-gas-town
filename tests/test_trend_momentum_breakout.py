import numpy as np

import jesse.helpers as jh
from jesse.config import config, reset_config
from jesse.enums import exchanges
from jesse.modes import backtest_mode
from jesse.store import store


def _build_candles(first_open: float, closes: list[float], volumes: list[float]) -> np.ndarray:
    timestamp = 1609459200000
    prev_close = first_open
    candles = []

    for close_price, volume in zip(closes, volumes):
        open_price = prev_close
        high_price = max(open_price, close_price) + 0.3
        low_price = min(open_price, close_price) - 0.3
        candles.append([timestamp, open_price, close_price, high_price, low_price, volume])
        prev_close = close_price
        timestamp += 60_000

    return np.array(candles, dtype=np.float64)


def _uptrend_closes() -> list[float]:
    price = 100.0
    closes = []

    for _ in range(50):
        price += 1.0
        closes.append(round(price, 4))
        price += 0.8
        closes.append(round(price, 4))
        price -= 0.7
        closes.append(round(price, 4))
        price += 0.9
        closes.append(round(price, 4))
        price -= 0.3
        closes.append(round(price, 4))

    closes.extend([price + 0.7, price + 1.2, price + 2.8, price + 4.9, price + 7.4, price + 10.1])
    return [round(c, 4) for c in closes]


def _downtrend_closes() -> list[float]:
    price = 320.0
    closes = []

    for _ in range(50):
        price -= 1.0
        closes.append(round(price, 4))
        price -= 0.8
        closes.append(round(price, 4))
        price += 0.7
        closes.append(round(price, 4))
        price -= 0.9
        closes.append(round(price, 4))
        price += 0.3
        closes.append(round(price, 4))

    closes.extend([price - 0.7, price - 1.2, price - 2.8, price - 4.9, price - 7.4, price - 10.1])
    return [round(c, 4) for c in closes]


def _run_backtest(candles: np.ndarray):
    reset_config()
    config['env']['exchanges'][exchanges.SANDBOX]['type'] = 'futures'
    config['env']['exchanges'][exchanges.SANDBOX]['balance'] = 10_000

    routes = [
        {'symbol': 'BTC-USDT', 'timeframe': '1m', 'strategy': 'TrendMomentumBreakout'}
    ]

    candle_map = {
        jh.key(exchanges.SANDBOX, 'BTC-USDT'): {
            'exchange': exchanges.SANDBOX,
            'symbol': 'BTC-USDT',
            'candles': candles
        }
    }

    backtest_mode.run('000', False, {}, exchanges.SANDBOX, routes, [], '2019-04-01', '2019-04-02', candle_map)


def test_trend_momentum_breakout_long_trade():
    closes = _uptrend_closes()
    volumes = [10.0] * (len(closes) - 4) + [12.0, 14.0, 30.0, 24.0]
    candles = _build_candles(100.0, closes, volumes)

    _run_backtest(candles)

    assert len(store.closed_trades.trades) == 1
    trade = store.closed_trades.trades[0]

    assert trade.type == 'long'
    assert trade.entry_price < trade.exit_price
    assert len(trade.orders) >= 3


def test_trend_momentum_breakout_short_trade():
    closes = _downtrend_closes()
    volumes = [10.0] * (len(closes) - 4) + [12.0, 14.0, 30.0, 24.0]
    candles = _build_candles(320.0, closes, volumes)

    _run_backtest(candles)

    assert len(store.closed_trades.trades) == 1
    trade = store.closed_trades.trades[0]

    assert trade.type == 'short'
    assert trade.entry_price > trade.exit_price
    assert len(trade.orders) >= 3


def test_trend_momentum_breakout_requires_volume_expansion():
    closes = _uptrend_closes()
    volumes = [10.0] * len(closes)
    candles = _build_candles(100.0, closes, volumes)

    _run_backtest(candles)

    assert len(store.closed_trades.trades) == 0
