import numpy as np

import jesse.indicators as ta
import jesse.utils as utils
from jesse.strategies.SyntheticRangeBarStrategy import SyntheticRangeBarStrategy


class RangeBarBreakoutPullbackScalp(SyntheticRangeBarStrategy):
    """
    Synthetic range-bar breakout-pullback scalp strategy.

    Route timeframe stays on 1m. Signals come from synthetic range bars.
    Exit model:
    - partial take-profit at tp1
    - runner target at tp2
    - trailing stop on the remainder after first reduction
    """

    def __init__(self) -> None:
        super().__init__()
        self.vars['signal_side'] = None
        self.vars['signal_stop'] = None
        self.vars['signal_tp1'] = None
        self.vars['signal_tp2'] = None
        self.vars['active_stop'] = None
        self.vars['runner_target'] = None

    def hyperparameters(self):
        return [
            {'name': 'range_size', 'type': int, 'min': 1, 'max': 25, 'default': 2},
            {'name': 'ema_period', 'type': int, 'min': 3, 'max': 50, 'default': 4},
            {'name': 'breakout_lookback', 'type': int, 'min': 2, 'max': 6, 'default': 2},
            {'name': 'position_size_pct', 'type': float, 'min': 0.01, 'max': 0.2, 'default': 0.03},
            {'name': 'tp1_r', 'type': float, 'min': 0.5, 'max': 3.0, 'default': 1.0},
            {'name': 'runner_r', 'type': float, 'min': 1.0, 'max': 6.0, 'default': 3.0},
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
        if len(bars) < self.hp['breakout_lookback'] + 3:
            return

        if self._detect_long_setup(bars):
            self._queue_signal('long', float(bars[-2][4]))
        elif self._detect_short_setup(bars):
            self._queue_signal('short', float(bars[-2][3]))

    def go_long(self):
        qty = self._position_qty()
        tp1_qty, runner_qty = self._split_qty(qty)

        self.buy = qty, self.price
        self.stop_loss = qty, self.vars['signal_stop']
        self.take_profit = [
            (tp1_qty, self.vars['signal_tp1']),
            (runner_qty, self.vars['signal_tp2']),
        ]

        self.vars['active_stop'] = self.vars['signal_stop']
        self.vars['runner_target'] = self.vars['signal_tp2']
        self.vars['signal_side'] = None

    def go_short(self):
        qty = self._position_qty()
        tp1_qty, runner_qty = self._split_qty(qty)

        self.sell = qty, self.price
        self.stop_loss = qty, self.vars['signal_stop']
        self.take_profit = [
            (tp1_qty, self.vars['signal_tp1']),
            (runner_qty, self.vars['signal_tp2']),
        ]

        self.vars['active_stop'] = self.vars['signal_stop']
        self.vars['runner_target'] = self.vars['signal_tp2']
        self.vars['signal_side'] = None

    def update_position(self):
        if self.position.is_close or self.reduced_count == 0 or len(self.synthetic_range_bars) == 0:
            return

        last_bar = self.synthetic_range_bars[-1]

        if self.is_long:
            next_stop = max(float(self.vars['active_stop']), float(last_bar[4]))
            if next_stop > float(self.vars['active_stop']):
                self.vars['active_stop'] = next_stop
                self.stop_loss = self.position.qty, next_stop
            self.take_profit = self.position.qty, float(self.vars['runner_target'])
        elif self.is_short:
            next_stop = min(float(self.vars['active_stop']), float(last_bar[3]))
            if next_stop < float(self.vars['active_stop']):
                self.vars['active_stop'] = next_stop
                self.stop_loss = self.position.qty, next_stop
            self.take_profit = self.position.qty, float(self.vars['runner_target'])

    def on_close_position(self, order, closed_trade):
        self.vars['active_stop'] = None
        self.vars['runner_target'] = None
        self.vars['signal_side'] = None

    def _queue_signal(self, side: str, stop_price: float) -> None:
        entry_price = float(self.price)

        if side == 'long':
            risk = entry_price - stop_price
        else:
            risk = stop_price - entry_price

        if risk <= 0:
            return

        self.vars['signal_side'] = side
        self.vars['signal_stop'] = stop_price
        self.vars['signal_tp1'] = entry_price + risk * self.hp['tp1_r'] if side == 'long' else entry_price - risk * self.hp['tp1_r']
        self.vars['signal_tp2'] = entry_price + risk * self.hp['runner_r'] if side == 'long' else entry_price - risk * self.hp['runner_r']

    def _position_qty(self) -> float:
        position_size = self.balance * self.hp['position_size_pct']
        precision = self._qty_rounding_precision()
        qty = utils.size_to_qty(position_size, self.price, precision=precision, fee_rate=self.fee_rate)
        min_qty = round(1 / (10 ** precision), precision)
        return max(qty, min_qty)

    def _split_qty(self, qty: float) -> tuple[float, float]:
        precision = self._qty_rounding_precision()
        tp1_qty = round(qty * 0.5, precision)
        runner_qty = round(qty - tp1_qty, precision)

        if tp1_qty <= 0 or runner_qty <= 0:
            return qty, qty

        return tp1_qty, runner_qty

    def _qty_rounding_precision(self) -> int:
        try:
            return self._qty_precision
        except KeyError:
            return 3

    def _trend_is_long(self) -> bool:
        candles = self.get_candles(self.exchange, self.symbol, '1m')
        if len(candles) < self.hp['ema_period']:
            return False
        return self.price > ta.ema(candles, self.hp['ema_period'])

    def _trend_is_short(self) -> bool:
        candles = self.get_candles(self.exchange, self.symbol, '1m')
        if len(candles) < self.hp['ema_period']:
            return False
        return self.price < ta.ema(candles, self.hp['ema_period'])

    def _detect_long_setup(self, bars: np.ndarray) -> bool:
        if not self._trend_is_long():
            return False

        breakout = bars[-3]
        pullback = bars[-2]
        confirm = bars[-1]
        prior = bars[-(self.hp['breakout_lookback'] + 3):-3]
        prior_high = prior[:, 3].max()

        return (
            self._is_bullish(breakout)
            and breakout[2] > prior_high
            and pullback[2] < breakout[2]
            and pullback[4] >= breakout[1]
            and self._is_bullish(confirm)
            and confirm[2] >= breakout[2]
        )

    def _detect_short_setup(self, bars: np.ndarray) -> bool:
        if not self._trend_is_short():
            return False

        breakout = bars[-3]
        pullback = bars[-2]
        confirm = bars[-1]
        prior = bars[-(self.hp['breakout_lookback'] + 3):-3]
        prior_low = prior[:, 4].min()

        return (
            self._is_bearish(breakout)
            and breakout[2] < prior_low
            and pullback[2] > breakout[2]
            and pullback[3] <= breakout[1]
            and self._is_bearish(confirm)
            and confirm[2] <= breakout[2]
        )

    @staticmethod
    def _is_bullish(bar: np.ndarray) -> bool:
        return float(bar[2]) >= float(bar[1])

    @staticmethod
    def _is_bearish(bar: np.ndarray) -> bool:
        return float(bar[2]) < float(bar[1])
