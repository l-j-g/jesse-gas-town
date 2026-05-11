from collections import namedtuple
from typing import Optional

import numpy as np

import jesse.indicators as ta
import jesse.utils as utils
from jesse.strategies import Strategy


BreakoutSignal = namedtuple('BreakoutSignal', ['side', 'stop', 'tp1', 'tp2'])


class TrendMomentumBreakout(Strategy):
    def __init__(self) -> None:
        super().__init__()
        self.vars['signal_side'] = None
        self.vars['signal_stop'] = None
        self.vars['signal_tp1'] = None
        self.vars['signal_tp2'] = None
        self.vars['active_stop'] = None
        self.vars['runner_target'] = None
        self.vars['last_exit_index'] = None

    def hyperparameters(self):
        return [
            {'name': 'fast_ema', 'type': int, 'min': 10, 'max': 30, 'default': 20},
            {'name': 'slow_ema', 'type': int, 'min': 30, 'max': 80, 'default': 50},
            {'name': 'regime_ema', 'type': int, 'min': 100, 'max': 250, 'default': 200},
            {'name': 'breakout_lookback', 'type': int, 'min': 10, 'max': 60, 'default': 20},
            {'name': 'swing_lookback', 'type': int, 'min': 5, 'max': 30, 'default': 10},
            {'name': 'volume_period', 'type': int, 'min': 10, 'max': 50, 'default': 20},
            {'name': 'volume_multiplier', 'type': float, 'min': 1.0, 'max': 2.0, 'default': 1.3},
            {'name': 'bb_dev', 'type': float, 'min': 1.5, 'max': 2.5, 'default': 2.0},
            {'name': 'position_size_pct', 'type': float, 'min': 0.01, 'max': 0.10, 'default': 0.03},
            {'name': 'tp1_r', 'type': float, 'min': 0.5, 'max': 2.0, 'default': 1.0},
            {'name': 'tp2_r', 'type': float, 'min': 1.0, 'max': 4.0, 'default': 2.2},
            {'name': 'cooldown_bars', 'type': int, 'min': 0, 'max': 20, 'default': 5},
        ]

    def should_long(self) -> bool:
        return self.vars['signal_side'] == 'long'

    def should_short(self) -> bool:
        return self.vars['signal_side'] == 'short'

    def should_cancel_entry(self):
        return False

    def before(self) -> None:
        self._reset_signal()

        if self.position.is_open:
            return
        if self._in_cooldown():
            return

        signal = self._detect_long_signal()
        if signal is not None:
            self._queue_signal(signal)
            return

        signal = self._detect_short_signal()
        if signal is not None:
            self._queue_signal(signal)

    def go_long(self) -> None:
        qty = self._position_qty()

        self.buy = qty, self.price
        self.stop_loss = qty, self.vars['signal_stop']
        self.take_profit = self._take_profit_orders(qty)
        self.vars['active_stop'] = self.vars['signal_stop']
        self.vars['runner_target'] = self.vars['signal_tp2']
        self.vars['signal_side'] = None

    def go_short(self) -> None:
        qty = self._position_qty()

        self.sell = qty, self.price
        self.stop_loss = qty, self.vars['signal_stop']
        self.take_profit = self._take_profit_orders(qty)
        self.vars['active_stop'] = self.vars['signal_stop']
        self.vars['runner_target'] = self.vars['signal_tp2']
        self.vars['signal_side'] = None

    def update_position(self) -> None:
        if self.position.is_close or self.reduced_count == 0:
            return

        fast_ema = self._ema(self.hp['fast_ema'])
        if not np.isfinite(fast_ema):
            return

        if self.is_long:
            next_stop = max(float(self.vars['active_stop']), float(fast_ema))
            if next_stop < self.price and next_stop > float(self.vars['active_stop']):
                self.vars['active_stop'] = next_stop
                self.stop_loss = self.position.qty, next_stop
            self.take_profit = self.position.qty, float(self.vars['runner_target'])
        elif self.is_short:
            next_stop = min(float(self.vars['active_stop']), float(fast_ema))
            if next_stop > self.price and next_stop < float(self.vars['active_stop']):
                self.vars['active_stop'] = next_stop
                self.stop_loss = self.position.qty, next_stop
            self.take_profit = self.position.qty, float(self.vars['runner_target'])

    def on_close_position(self, order, closed_trade) -> None:
        self._reset_signal()
        self.vars['active_stop'] = None
        self.vars['runner_target'] = None
        self.vars['last_exit_index'] = self.index

    def _detect_long_signal(self) -> Optional[BreakoutSignal]:
        candles = self.candles
        if len(candles) < self._required_candles():
            return None

        close_price = float(candles[-1][2])
        previous_close = float(candles[-2][2])
        fast_ema = self._ema(self.hp['fast_ema'])
        slow_ema = self._ema(self.hp['slow_ema'])
        regime_ema = self._ema(self.hp['regime_ema'])
        if not np.isfinite(fast_ema) or not np.isfinite(slow_ema) or not np.isfinite(regime_ema):
            return None

        if not (close_price > fast_ema > slow_ema > regime_ema):
            return None

        rsi = ta.rsi(candles, 14, sequential=True)
        if not np.isfinite(rsi[-1]) or rsi[-1] < 50:
            return None

        volume = ta.volume(candles, period=self.hp['volume_period'], sequential=True)
        if not np.isfinite(volume.ma[-1]) or volume.ma[-1] <= 0:
            return None
        if volume.volume[-1] < volume.ma[-1] * self.hp['volume_multiplier']:
            return None

        macd = ta.macd(candles, 12, 26, 9, sequential=True)
        if not self._macd_supports_long(macd):
            return None

        bb = ta.bollinger_bands(
            candles,
            period=20,
            devup=self.hp['bb_dev'],
            devdn=self.hp['bb_dev'],
            sequential=True,
        )
        if not np.isfinite(bb.upperband[-1]):
            return None

        resistance = self._rolling_resistance()
        if previous_close > resistance or close_price <= resistance:
            return None

        if close_price < float(bb.upperband[-1]):
            return None

        stop_price = max(self._recent_swing_low(), resistance)
        if stop_price >= close_price:
            return None

        risk = close_price - stop_price
        return BreakoutSignal(
            'long',
            stop_price,
            close_price + risk * self.hp['tp1_r'],
            close_price + risk * self.hp['tp2_r'],
        )

    def _detect_short_signal(self) -> Optional[BreakoutSignal]:
        candles = self.candles
        if len(candles) < self._required_candles():
            return None

        close_price = float(candles[-1][2])
        previous_close = float(candles[-2][2])
        fast_ema = self._ema(self.hp['fast_ema'])
        slow_ema = self._ema(self.hp['slow_ema'])
        regime_ema = self._ema(self.hp['regime_ema'])
        if not np.isfinite(fast_ema) or not np.isfinite(slow_ema) or not np.isfinite(regime_ema):
            return None

        if not (close_price < fast_ema < slow_ema < regime_ema):
            return None

        rsi = ta.rsi(candles, 14, sequential=True)
        if not np.isfinite(rsi[-1]) or rsi[-1] > 50:
            return None

        volume = ta.volume(candles, period=self.hp['volume_period'], sequential=True)
        if not np.isfinite(volume.ma[-1]) or volume.ma[-1] <= 0:
            return None
        if volume.volume[-1] < volume.ma[-1] * self.hp['volume_multiplier']:
            return None

        macd = ta.macd(candles, 12, 26, 9, sequential=True)
        if not self._macd_supports_short(macd):
            return None

        bb = ta.bollinger_bands(
            candles,
            period=20,
            devup=self.hp['bb_dev'],
            devdn=self.hp['bb_dev'],
            sequential=True,
        )
        if not np.isfinite(bb.lowerband[-1]):
            return None

        support = self._rolling_support()
        if previous_close < support or close_price >= support:
            return None

        if close_price > float(bb.lowerband[-1]):
            return None

        stop_price = min(self._recent_swing_high(), support)
        if stop_price <= close_price:
            return None

        risk = stop_price - close_price
        return BreakoutSignal(
            'short',
            stop_price,
            close_price - risk * self.hp['tp1_r'],
            close_price - risk * self.hp['tp2_r'],
        )

    def _queue_signal(self, signal: BreakoutSignal) -> None:
        self.vars['signal_side'] = signal.side
        self.vars['signal_stop'] = signal.stop
        self.vars['signal_tp1'] = signal.tp1
        self.vars['signal_tp2'] = signal.tp2

    def _take_profit_orders(self, qty: float):
        precision = self._qty_rounding_precision()
        partial_qty = round(qty * 0.5, precision)
        runner_qty = round(qty - partial_qty, precision)

        if partial_qty <= 0 or runner_qty <= 0:
            return qty, self.vars['signal_tp2']

        return [
            (partial_qty, self.vars['signal_tp1']),
            (runner_qty, self.vars['signal_tp2']),
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

    def _required_candles(self) -> int:
        return max(
            self.hp['regime_ema'] + 2,
            self.hp['breakout_lookback'] + 2,
            self.hp['swing_lookback'] + 2,
            self.hp['volume_period'] + 2,
            35,
        )

    def _ema(self, period: int) -> float:
        return float(ta.ema(self.candles, period))

    def _rolling_resistance(self) -> float:
        highs = self.candles[-self.hp['breakout_lookback'] - 1:-1, 3]
        return float(np.max(highs))

    def _rolling_support(self) -> float:
        lows = self.candles[-self.hp['breakout_lookback'] - 1:-1, 4]
        return float(np.min(lows))

    def _recent_swing_low(self) -> float:
        lows = self.candles[-self.hp['swing_lookback'] - 1:-1, 4]
        return float(np.min(lows))

    def _recent_swing_high(self) -> float:
        highs = self.candles[-self.hp['swing_lookback'] - 1:-1, 3]
        return float(np.max(highs))

    def _reset_signal(self) -> None:
        self.vars['signal_side'] = None
        self.vars['signal_stop'] = None
        self.vars['signal_tp1'] = None
        self.vars['signal_tp2'] = None

    def _in_cooldown(self) -> bool:
        last_exit_index = self.vars['last_exit_index']
        if last_exit_index is None:
            return False
        return self.index - int(last_exit_index) <= self.hp['cooldown_bars']

    @staticmethod
    def _macd_supports_long(macd) -> bool:
        return bool(
            np.isfinite(macd.macd[-1])
            and np.isfinite(macd.signal[-1])
            and np.isfinite(macd.hist[-1])
            and np.isfinite(macd.hist[-2])
            and macd.macd[-1] > macd.signal[-1] > 0
            and macd.hist[-1] > 0
            and macd.hist[-1] >= macd.hist[-2]
        )

    @staticmethod
    def _macd_supports_short(macd) -> bool:
        return bool(
            np.isfinite(macd.macd[-1])
            and np.isfinite(macd.signal[-1])
            and np.isfinite(macd.hist[-1])
            and np.isfinite(macd.hist[-2])
            and macd.macd[-1] < macd.signal[-1] < 0
            and macd.hist[-1] < 0
            and macd.hist[-1] <= macd.hist[-2]
        )
