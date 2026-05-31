from collections import namedtuple
import importlib

import numpy as np

from jesse.testing_utils import single_route_backtest
from jesse.strategies.FailedBreakoutValueFade import FailedBreakoutValueFade


Channel = namedtuple('Channel', ['upperband', 'middleband', 'lowerband'])
strategy_module = importlib.import_module('jesse.strategies.FailedBreakoutValueFade')


def _default_hp() -> dict:
    strategy = FailedBreakoutValueFade()
    return {item['name']: item['default'] for item in strategy.hyperparameters()}


def _candles(rows: list[list[float]]) -> np.ndarray:
    return np.array(rows, dtype=np.float64)


def test_failed_breakout_value_fade_detects_long_rejection(monkeypatch):
    strategy = FailedBreakoutValueFade()
    strategy.hp = _default_hp()
    candles = _candles([
        [1, 100, 99, 101, 98, 1],
        [2, 99, 98, 100, 97, 1],
        [3, 98, 97, 99, 96, 1],
        [4, 97, 96, 98, 95, 1],
        [5, 96, 94, 97, 93, 1],
        [6, 94, 97, 98, 94, 1],
    ])

    monkeypatch.setattr(strategy_module.ta, 'donchian', lambda *args, **kwargs: Channel(
        np.array([105, 104, 103, 102, 101, 100], dtype=np.float64),
        np.array([100, 100, 99, 99, 98, 98], dtype=np.float64),
        np.array([96, 96, 95, 95, 95, 95], dtype=np.float64),
    ))
    monkeypatch.setattr(strategy_module.ta, 'adx', lambda *args, **kwargs: 15.0)
    monkeypatch.setattr(strategy_module.ta, 'willr', lambda *args, **kwargs: -88.0)
    monkeypatch.setattr(strategy_module.ta, 'atr', lambda *args, **kwargs: 2.0)
    monkeypatch.setattr(strategy_module.ta, 'vwap', lambda *args, **kwargs: np.array([99, 99, 99, 99, 98.5, 98.5], dtype=np.float64))

    signal = strategy._detect_long_setup(candles)

    assert signal is not None
    assert signal.stop == 91.5
    assert signal.target == 98.0


def test_failed_breakout_value_fade_detects_short_rejection(monkeypatch):
    strategy = FailedBreakoutValueFade()
    strategy.hp = _default_hp()
    candles = _candles([
        [1, 100, 101, 102, 99, 1],
        [2, 101, 102, 103, 100, 1],
        [3, 102, 103, 104, 101, 1],
        [4, 103, 104, 105, 102, 1],
        [5, 104, 107, 108, 104, 1],
        [6, 107, 103, 107, 102, 1],
    ])

    monkeypatch.setattr(strategy_module.ta, 'donchian', lambda *args, **kwargs: Channel(
        np.array([103, 104, 105, 106, 106, 106], dtype=np.float64),
        np.array([100, 100, 101, 101, 102, 102], dtype=np.float64),
        np.array([97, 97, 98, 98, 99, 99], dtype=np.float64),
    ))
    monkeypatch.setattr(strategy_module.ta, 'adx', lambda *args, **kwargs: 16.0)
    monkeypatch.setattr(strategy_module.ta, 'willr', lambda *args, **kwargs: -12.0)
    monkeypatch.setattr(strategy_module.ta, 'atr', lambda *args, **kwargs: 2.0)
    monkeypatch.setattr(strategy_module.ta, 'vwap', lambda *args, **kwargs: np.array([101, 101, 101, 101, 102, 101], dtype=np.float64))

    signal = strategy._detect_short_setup(candles)

    assert signal is not None
    assert signal.stop == 109.5
    assert signal.target == 102.0


def test_failed_breakout_value_fade_go_short_sets_orders(monkeypatch):
    strategy = FailedBreakoutValueFade()
    strategy.vars['signal_side'] = 'short'
    strategy.vars['signal_stop'] = 108.0
    strategy.vars['signal_target'] = 99.0

    monkeypatch.setattr(FailedBreakoutValueFade, 'price', property(lambda self: 103.0))
    monkeypatch.setattr(FailedBreakoutValueFade, '_position_qty', lambda self, stop_price: 0.75)

    strategy.go_short()

    assert strategy.sell == (0.75, 103.0)
    assert strategy.stop_loss == (0.75, 108.0)
    assert strategy.take_profit == (0.75, 99.0)
    assert strategy.vars['signal_side'] is None


def test_failed_breakout_value_fade_backtest_smoke():
    single_route_backtest('FailedBreakoutValueFade', candles_count=140, timeframe='1m')
