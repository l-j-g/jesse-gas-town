from collections import namedtuple
from typing import Optional

import numpy as np

import jesse.indicators as ta
import jesse.utils as utils
from jesse.strategies.SyntheticRangeBarStrategy import SyntheticRangeBarStrategy


MeanReversionSignal = namedtuple('MeanReversionSignal', ['stop', 'target'])


class RangeBarBollingerMeanReversion(SyntheticRangeBarStrategy):
    """
    Synthetic range-bar Bollinger Band mean-reversion strategy.

    Route timeframe stays on 1m. Bollinger Bands, regime filtering, triggers,
    stops, and targets are all calculated from synthetic range bars.
    """

    def __init__(self) -> None:
        super().__init__()
        self.vars['signal_side'] = None
        self.vars['signal_stop'] = None
        self.vars['signal_tp1'] = None
        self.vars['signal_tp2'] = None

    def hyperparameters(self):
        return [
            {'name': 'range_size', 'type': int, 'min': 1, 'max': 25, 'default': 2},
            {'name': 'bb_period', 'type': int, 'min': 10, 'max': 50, 'default': 20},
            {'name': 'bb_mult', 'type': float, 'min': 1.5, 'max': 3.0, 'default': 2.0},
            {'name': 'max_band_width_pct', 'type': float, 'min': 0.01, 'max': 0.08, 'default': 0.035},
            {'name': 'entry_reclaim_bars', 'type': int, 'min': 1, 'max': 3, 'default': 1},
            {'name': 'stop_buffer_ranges', 'type': float, 'min': 0.5, 'max': 3.0, 'default': 1.0},
            {'name': 'position_size_pct', 'type': float, 'min': 0.01, 'max': 0.10, 'default': 0.025},
            {'name': 'partial_qty_pct', 'type': float, 'min': 0.25, 'max': 0.75, 'default': 0.5},
        ]

    def synthetic_range_bar_size(self) -> float:
        return self.hp['range_size']

    def should_long(self):
        return self.vars['signal_side'] == 'long'

    def should_short(self):
        return self.vars['signal_side'] == 'short'

    def should_cancel_entry(self):
        return False

    def before(self) -> None:
        super().before()

        self.vars['signal_side'] = None
        self.vars['signal_stop'] = None
        self.vars['signal_tp1'] = None
        self.vars['signal_tp2'] = None

        if self.position.is_open:
            return

        bars = self.synthetic_range_bars
        required_bars = self.hp['bb_period'] + self.hp['entry_reclaim_bars'] + 1
        if len(bars) < required_bars:
            return

        long_signal = self._detect_long_setup(bars)
        if long_signal is not None:
            self._queue_signal('long', long_signal.stop, long_signal.target)
            return

        short_signal = self._detect_short_setup(bars)
        if short_signal is not None:
            self._queue_signal('short', short_signal.stop, short_signal.target)

    def go_long(self):
        qty = self._position_qty()

        self.buy = qty, self.price
        self.stop_loss = qty, self.vars['signal_stop']
        self.take_profit = self._take_profit_orders(qty)
        self.vars['signal_side'] = None

    def go_short(self):
        qty = self._position_qty()

        self.sell = qty, self.price
        self.stop_loss = qty, self.vars['signal_stop']
        self.take_profit = self._take_profit_orders(qty)
        self.vars['signal_side'] = None

    def on_close_position(self, order, closed_trade):
        self.vars['signal_side'] = None
        self.vars['signal_stop'] = None
        self.vars['signal_tp1'] = None
        self.vars['signal_tp2'] = None

    def _detect_long_setup(self, bars: np.ndarray) -> Optional[MeanReversionSignal]:
        bb = self._bb(bars)
        if not self._bands_are_usable(bb):
            return None

        if self._band_width_pct(bb) > self.hp['max_band_width_pct']:
            return None

        previous_indexes = self._previous_trigger_indexes(bars)
        lower_breach = any(
            bars[i][2] <= bb.lowerband[i] or bars[i][4] <= bb.lowerband[i]
            for i in previous_indexes
        )
        latest_close = float(bars[-1][2])
        latest_lower = float(bb.lowerband[-1])
        latest_middle = float(bb.middleband[-1])

        if not lower_breach or latest_close <= latest_lower or latest_close >= latest_middle:
            return None

        if latest_middle <= self.price:
            return None

        recent = bars[-(self.hp['entry_reclaim_bars'] + 1):]
        stop = float(recent[:, 4].min()) - self.hp['range_size'] * self.hp['stop_buffer_ranges']
        if self.price - stop <= 0:
            return None

        return MeanReversionSignal(stop, latest_middle)

    def _detect_short_setup(self, bars: np.ndarray) -> Optional[MeanReversionSignal]:
        bb = self._bb(bars)
        if not self._bands_are_usable(bb):
            return None

        if self._band_width_pct(bb) > self.hp['max_band_width_pct']:
            return None

        previous_indexes = self._previous_trigger_indexes(bars)
        upper_breach = any(
            bars[i][2] >= bb.upperband[i] or bars[i][3] >= bb.upperband[i]
            for i in previous_indexes
        )
        latest_close = float(bars[-1][2])
        latest_upper = float(bb.upperband[-1])
        latest_middle = float(bb.middleband[-1])

        if not upper_breach or latest_close >= latest_upper or latest_close <= latest_middle:
            return None

        if latest_middle >= self.price:
            return None

        recent = bars[-(self.hp['entry_reclaim_bars'] + 1):]
        stop = float(recent[:, 3].max()) + self.hp['range_size'] * self.hp['stop_buffer_ranges']
        if stop - self.price <= 0:
            return None

        return MeanReversionSignal(stop, latest_middle)

    def _queue_signal(self, side: str, stop_price: float, target_price: float) -> None:
        entry_price = float(self.price)

        if side == 'long' and target_price <= entry_price:
            return
        if side == 'short' and target_price >= entry_price:
            return

        self.vars['signal_side'] = side
        self.vars['signal_stop'] = stop_price
        self.vars['signal_tp1'] = entry_price + (target_price - entry_price) * 0.5
        self.vars['signal_tp2'] = target_price

    def _take_profit_orders(self, qty: float):
        precision = self._qty_rounding_precision()
        partial_qty = round(qty * self.hp['partial_qty_pct'], precision)
        final_qty = round(qty - partial_qty, precision)

        if partial_qty <= 0 or final_qty <= 0:
            return qty, self.vars['signal_tp2']

        return [
            (partial_qty, self.vars['signal_tp1']),
            (final_qty, self.vars['signal_tp2']),
        ]

    def _position_qty(self) -> float:
        position_size = self.balance * self.hp['position_size_pct']
        precision = self._qty_rounding_precision()
        qty = utils.size_to_qty(position_size, self.price, precision=precision, fee_rate=self.fee_rate)
        min_qty = round(1 / (10 ** precision), precision)
        return max(qty, min_qty)

    def _qty_rounding_precision(self) -> int:
        try:
            return self._qty_precision
        except KeyError:
            return 3

    def _bb(self, bars: np.ndarray):
        return ta.bollinger_bands(
            bars,
            period=self.hp['bb_period'],
            devup=self.hp['bb_mult'],
            devdn=self.hp['bb_mult'],
            sequential=True,
        )

    def _bands_are_usable(self, bb) -> bool:
        return bool(
            np.isfinite(bb.upperband[-1])
            and np.isfinite(bb.middleband[-1])
            and np.isfinite(bb.lowerband[-1])
            and bb.middleband[-1] > 0
        )

    def _band_width_pct(self, bb) -> float:
        return float((bb.upperband[-1] - bb.lowerband[-1]) / abs(bb.middleband[-1]))

    def _previous_trigger_indexes(self, bars: np.ndarray) -> range:
        start = len(bars) - self.hp['entry_reclaim_bars'] - 1
        return range(start, len(bars) - 1)
