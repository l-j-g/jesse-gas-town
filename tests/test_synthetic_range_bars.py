import numpy as np
import pytest

from jesse import exceptions
from jesse.enums import exchanges
from jesse.routes import router
from jesse.services import candle_service
from jesse.services.synthetic_range_bar import SyntheticRangeBarBuilder
from jesse.store import store
from jesse.testing_utils import single_route_backtest


def test_builder_updates_forming_bar_without_completion():
    builder = SyntheticRangeBarBuilder(range_size=2, max_bars=10)
    candle = np.array([1, 100, 101, 101.5, 99.5, 9], dtype=np.float64)

    completed = builder.update(candle)

    assert completed == []
    np.testing.assert_allclose(builder.forming_bar, np.array([1, 100, 101, 101.5, 99.5, 9], dtype=np.float64))
    assert builder.processed_count == 1


def test_builder_uses_jesse_intrabar_path_for_bearish_candles():
    builder = SyntheticRangeBarBuilder(range_size=1, max_bars=10)
    candle = np.array([1, 100, 99, 101.2, 98.5, 20], dtype=np.float64)

    completed = builder.update(candle)

    assert len(completed) == 3
    np.testing.assert_allclose(completed[0][:5], np.array([1, 100, 101, 101, 100], dtype=np.float64))
    np.testing.assert_allclose(completed[1][:5], np.array([1, 101, 100, 101.2, 100], dtype=np.float64))
    np.testing.assert_allclose(completed[2][:5], np.array([1, 100, 99, 100, 99], dtype=np.float64))
    np.testing.assert_allclose(
        builder.forming_bar[:5],
        np.array([1, 99, 99, 99, 98.5], dtype=np.float64),
    )
    assert pytest.approx(sum(bar[5] for bar in completed) + builder.forming_bar[5], rel=1e-9) == candle[5]


def test_builder_handles_gap_opens_without_double_counting_volume():
    builder = SyntheticRangeBarBuilder(range_size=1, max_bars=10)

    builder.update(np.array([1, 100, 100.5, 100.5, 100, 7], dtype=np.float64))
    completed = builder.update(np.array([2, 103, 103.2, 103.2, 103, 8], dtype=np.float64))

    assert len(completed) == 3
    np.testing.assert_allclose(completed[0][:5], np.array([1, 100, 101, 101, 100], dtype=np.float64))
    np.testing.assert_allclose(completed[1][:5], np.array([2, 101, 102, 102, 101], dtype=np.float64))
    np.testing.assert_allclose(completed[2][:5], np.array([2, 102, 103, 103, 102], dtype=np.float64))
    assert pytest.approx(builder.completed_bars[:, 5].sum() + builder.forming_bar[5], rel=1e-9) == 15


def test_builder_ignores_duplicate_timestamps():
    builder = SyntheticRangeBarBuilder(range_size=1, max_bars=10)
    candle = np.array([1, 100, 101, 101, 100, 3], dtype=np.float64)

    first = builder.update(candle)
    second = builder.update(candle.copy())

    assert len(first) == 1
    assert second == []
    assert builder.processed_count == 1
    assert len(builder.completed_bars) == 1


def test_synthetic_range_bar_strategy_processes_each_1m_once():
    single_route_backtest('TestSyntheticRangeBarStrategy', candles_count=60, timeframe='1m')

    strategy = router.routes[0].strategy
    one_minute_candles = candle_service.get_candles(exchanges.SANDBOX, 'BTC-USDT', '1m')

    assert strategy.synthetic_range_processed_count == len(one_minute_candles)
    assert strategy.synthetic_range_last_processed_1m == one_minute_candles[-1][0]
    assert len(strategy.synthetic_range_bars) >= 2
    assert strategy.vars['entry_count'] == 1
    assert len(store.closed_trades.trades) == 1


def test_synthetic_range_bar_strategy_requires_1m_route():
    with pytest.raises(exceptions.InvalidStrategy):
        single_route_backtest('TestSyntheticRangeBarStrategy', candles_count=60, timeframe='5m')
