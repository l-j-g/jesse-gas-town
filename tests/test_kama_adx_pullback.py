from collections import namedtuple
import importlib

import numpy as np

from jesse.testing_utils import single_route_backtest
from jesse.strategies.KamaAdxPullback import KamaAdxPullback


DI = namedtuple('DI', ['plus', 'minus'])
strategy_module = importlib.import_module('jesse.strategies.KamaAdxPullback')


def _default_hp() -> dict:
    strategy = KamaAdxPullback()
    return {item['name']: item['default'] for item in strategy.hyperparameters()}


def _candles(rows: list[list[float]]) -> np.ndarray:
    return np.array(rows, dtype=np.float64)


def test_kama_adx_pullback_detects_long_reclaim(monkeypatch):
    strategy = KamaAdxPullback()
    strategy.hp = _default_hp()
    strategy.hp['pullback_lookback'] = 3
    candles = _candles([
        [1, 100, 101, 102, 99, 1],
        [2, 101, 103, 104, 100, 1],
        [3, 103, 106, 107, 102, 1],
        [4, 106, 104, 107, 103, 1],
        [5, 104, 105, 106, 103, 1],
        [6, 105, 108, 109, 104, 1],
    ])

    monkeypatch.setattr(strategy_module.ta, 'kama', lambda *args, **kwargs: np.array([99, 100, 101, 103, 104, 105], dtype=np.float64))
    monkeypatch.setattr(strategy_module.ta, 'adx', lambda *args, **kwargs: 28.0)
    monkeypatch.setattr(strategy_module.ta, 'di', lambda *args, **kwargs: DI(
        np.array([20, 22, 24, 23, 24, 30], dtype=np.float64),
        np.array([18, 17, 16, 15, 14, 12], dtype=np.float64),
    ))
    monkeypatch.setattr(strategy_module.ta, 'atr', lambda *args, **kwargs: 2.0)

    signal = strategy._detect_long_setup(candles)

    assert signal is not None
    assert signal.stop == 99.6
    assert signal.target > candles[-1][2]


def test_kama_adx_pullback_detects_short_reclaim(monkeypatch):
    strategy = KamaAdxPullback()
    strategy.hp = _default_hp()
    strategy.hp['pullback_lookback'] = 3
    candles = _candles([
        [1, 110, 109, 111, 108, 1],
        [2, 109, 107, 110, 106, 1],
        [3, 107, 104, 108, 103, 1],
        [4, 104, 106, 107, 104, 1],
        [5, 106, 105, 107, 104, 1],
        [6, 105, 102, 106, 101, 1],
    ])

    monkeypatch.setattr(strategy_module.ta, 'kama', lambda *args, **kwargs: np.array([111, 110, 109, 107, 106, 105], dtype=np.float64))
    monkeypatch.setattr(strategy_module.ta, 'adx', lambda *args, **kwargs: 27.0)
    monkeypatch.setattr(strategy_module.ta, 'di', lambda *args, **kwargs: DI(
        np.array([15, 14, 13, 12, 11, 10], dtype=np.float64),
        np.array([18, 19, 20, 21, 22, 26], dtype=np.float64),
    ))
    monkeypatch.setattr(strategy_module.ta, 'atr', lambda *args, **kwargs: 2.0)

    signal = strategy._detect_short_setup(candles)

    assert signal is not None
    assert signal.stop == 110.4
    assert signal.target < candles[-1][2]


def test_kama_adx_pullback_go_long_sets_orders(monkeypatch):
    strategy = KamaAdxPullback()
    strategy.vars['signal_side'] = 'long'
    strategy.vars['signal_stop'] = 95.0
    strategy.vars['signal_target'] = 112.0

    monkeypatch.setattr(KamaAdxPullback, 'price', property(lambda self: 100.0))
    monkeypatch.setattr(KamaAdxPullback, '_position_qty', lambda self, stop_price: 1.25)

    strategy.go_long()

    assert strategy.buy == (1.25, 100.0)
    assert strategy.stop_loss == (1.25, 95.0)
    assert strategy.take_profit == (1.25, 112.0)
    assert strategy.vars['signal_side'] is None


def test_kama_adx_pullback_backtest_smoke():
    single_route_backtest('KamaAdxPullback', candles_count=140, timeframe='1m')
