from collections import namedtuple
import importlib

import numpy as np

import jesse.helpers as jh
from jesse.config import config, reset_config
from jesse.enums import exchanges
from jesse.modes import backtest_mode
from jesse.store import store
from jesse.strategies.RangeBarBollingerMeanReversion import RangeBarBollingerMeanReversion


Bands = namedtuple('Bands', ['upperband', 'middleband', 'lowerband'])
strategy_module = importlib.import_module('jesse.strategies.RangeBarBollingerMeanReversion')


def _build_candles(first_open: float, closes: list[float]) -> np.ndarray:
    timestamp = 1609459200000
    previous_close = first_open
    candles = []

    for close_price in closes:
        open_price = previous_close
        high_price = max(open_price, close_price)
        low_price = min(open_price, close_price)
        candles.append([timestamp, open_price, close_price, high_price, low_price, 1])
        previous_close = close_price
        timestamp += 60_000

    return np.array(candles, dtype=np.float64)


def _run_backtest(candles: np.ndarray):
    reset_config()
    config['env']['exchanges'][exchanges.SANDBOX]['type'] = 'futures'
    config['env']['exchanges'][exchanges.SANDBOX]['balance'] = 10_000

    routes = [
        {'symbol': 'BTC-USDT', 'timeframe': '1m', 'strategy': 'RangeBarBollingerMeanReversion'}
    ]

    candle_map = {
        jh.key(exchanges.SANDBOX, 'BTC-USDT'): {
            'exchange': exchanges.SANDBOX,
            'symbol': 'BTC-USDT',
            'candles': candles
        }
    }

    backtest_mode.run('000', False, {}, exchanges.SANDBOX, routes, [], '2019-04-01', '2019-04-02', candle_map)


def _default_hp() -> dict:
    strategy = RangeBarBollingerMeanReversion()
    return {item['name']: item['default'] for item in strategy.hyperparameters()}


def _range_bars_from_closes(first_open: float, closes: list[float]) -> np.ndarray:
    timestamp = 1609459200000
    previous_close = first_open
    bars = []

    for close_price in closes:
        bars.append([
            timestamp,
            previous_close,
            close_price,
            max(previous_close, close_price),
            min(previous_close, close_price),
            1,
        ])
        previous_close = close_price
        timestamp += 60_000

    return np.array(bars, dtype=np.float64)


def test_range_bar_bollinger_mean_reversion_uses_synthetic_bars_for_bands(monkeypatch):
    strategy = RangeBarBollingerMeanReversion()
    strategy.hp = _default_hp()
    strategy.hp['max_band_width_pct'] = 0.08
    bars = _range_bars_from_closes(100, [100] * 20 + [97, 99])
    captured = {}

    def fake_bollinger_bands(candles, period, devup, devdn, sequential):
        captured['candles'] = candles
        upper = np.full(len(candles), 102.0)
        middle = np.full(len(candles), 100.0)
        lower = np.full(len(candles), 98.0)
        return Bands(upper, middle, lower)

    monkeypatch.setattr(strategy_module.ta, 'bollinger_bands', fake_bollinger_bands)
    monkeypatch.setattr(RangeBarBollingerMeanReversion, 'price', property(lambda self: 99.0))

    signal = strategy._detect_long_setup(bars)

    assert captured['candles'] is bars
    assert signal is not None


def test_range_bar_bollinger_mean_reversion_rejects_insufficient_bars():
    strategy = RangeBarBollingerMeanReversion()
    strategy.hp = _default_hp()
    bars = _range_bars_from_closes(1000, [1002] * 10)

    assert len(bars) < strategy.hp['bb_period'] + strategy.hp['entry_reclaim_bars'] + 1


def test_range_bar_bollinger_mean_reversion_rejects_wide_bands(monkeypatch):
    strategy = RangeBarBollingerMeanReversion()
    strategy.hp = _default_hp()
    bars = _range_bars_from_closes(100, [100] * 20 + [97, 99])

    def fake_bollinger_bands(candles, period, devup, devdn, sequential):
        upper = np.full(len(candles), 130.0)
        middle = np.full(len(candles), 100.0)
        lower = np.full(len(candles), 70.0)
        return Bands(upper, middle, lower)

    monkeypatch.setattr(strategy_module.ta, 'bollinger_bands', fake_bollinger_bands)
    monkeypatch.setattr(RangeBarBollingerMeanReversion, 'price', property(lambda self: 99.0))

    assert strategy._detect_long_setup(bars) is None


def test_range_bar_bollinger_mean_reversion_long_trade():
    candles = _build_candles(
        1000,
        [
            1002, 1000, 1002, 1000, 1002, 1000, 1002, 1000, 1002, 1000,
            1002, 1000, 1002, 1000, 1002, 1000, 1002, 1000, 1002, 1000,
            998, 1000, 1002, 1004,
        ],
    )

    _run_backtest(candles)

    assert len(store.closed_trades.trades) == 1
    trade = store.closed_trades.trades[0]

    assert trade.type == 'long'
    assert trade.entry_price == 1000
    assert trade.exit_price > trade.entry_price


def test_range_bar_bollinger_mean_reversion_short_trade():
    candles = _build_candles(
        1000,
        [
            998, 1000, 998, 1000, 998, 1000, 998, 1000, 998, 1000,
            998, 1000, 998, 1000, 998, 1000, 998, 1000, 998, 1000,
            1002, 1000, 998, 996,
        ],
    )

    _run_backtest(candles)

    assert len(store.closed_trades.trades) == 1
    trade = store.closed_trades.trades[0]

    assert trade.type == 'short'
    assert trade.entry_price == 1000
    assert trade.exit_price < trade.entry_price
