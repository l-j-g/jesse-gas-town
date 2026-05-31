from collections import namedtuple
from typing import Optional

import numpy as np

import jesse.indicators as ta
import jesse.utils as utils
from jesse.strategies.Strategy import Strategy


FadeSignal = namedtuple('FadeSignal', ['stop', 'target'])


class FailedBreakoutValueFade(Strategy):
    def __init__(self) -> None:
        super().__init__()
        self.vars['signal_side'] = None
        self.vars['signal_stop'] = None
        self.vars['signal_target'] = None

    def hyperparameters(self):
        return [
            {'name': 'donchian_period', 'type': int, 'min': 10, 'max': 55, 'default': 20},
            {'name': 'adx_period', 'type': int, 'min': 7, 'max': 28, 'default': 14},
            {'name': 'max_adx', 'type': float, 'min': 10.0, 'max': 30.0, 'default': 18.0},
            {'name': 'willr_period', 'type': int, 'min': 7, 'max': 28, 'default': 14},
            {'name': 'willr_long_threshold', 'type': float, 'min': -95.0, 'max': -60.0, 'default': -80.0},
            {'name': 'willr_short_threshold', 'type': float, 'min': -40.0, 'max': -5.0, 'default': -20.0},
            {'name': 'atr_period', 'type': int, 'min': 7, 'max': 28, 'default': 14},
            {'name': 'stop_atr_buffer', 'type': float, 'min': 0.25, 'max': 2.0, 'default': 0.75},
            {'name': 'risk_per_trade_pct', 'type': float, 'min': 0.1, 'max': 2.0, 'default': 0.5},
        ]

    def should_long(self):
        return self.vars['signal_side'] == 'long'

    def should_short(self):
        return self.vars['signal_side'] == 'short'

    def should_cancel_entry(self):
        return False

    def before(self) -> None:
        self.vars['signal_side'] = None
        self.vars['signal_stop'] = None
        self.vars['signal_target'] = None

        if self.position.is_open:
            return

        candles = self.candles
        required = max(
            self.hp['donchian_period'],
            self.hp['adx_period'] * 2,
            self.hp['willr_period'],
            self.hp['atr_period'],
        ) + 2
        if len(candles) < required:
            return

        long_signal = self._detect_long_setup(candles)
        if long_signal is not None:
            self._queue_signal('long', long_signal.stop, long_signal.target)
            return

        short_signal = self._detect_short_setup(candles)
        if short_signal is not None:
            self._queue_signal('short', short_signal.stop, short_signal.target)

    def go_long(self):
        qty = self._position_qty(self.vars['signal_stop'])

        self.buy = qty, self.price
        self.stop_loss = qty, self.vars['signal_stop']
        self.take_profit = qty, self.vars['signal_target']
        self.vars['signal_side'] = None

    def go_short(self):
        qty = self._position_qty(self.vars['signal_stop'])

        self.sell = qty, self.price
        self.stop_loss = qty, self.vars['signal_stop']
        self.take_profit = qty, self.vars['signal_target']
        self.vars['signal_side'] = None

    def on_close_position(self, order, closed_trade):
        self.vars['signal_side'] = None
        self.vars['signal_stop'] = None
        self.vars['signal_target'] = None

    def _detect_long_setup(self, candles: np.ndarray) -> Optional[FadeSignal]:
        channel = ta.donchian(candles, period=self.hp['donchian_period'], sequential=True)
        adx = ta.adx(candles, period=self.hp['adx_period'])
        willr = ta.willr(candles, period=self.hp['willr_period'])
        atr = ta.atr(candles, period=self.hp['atr_period'])
        vwap = ta.vwap(candles, sequential=True)
        if not self._value_inputs_are_usable(channel, adx, willr, atr, vwap):
            return None

        previous = candles[-2]
        current = candles[-1]
        entry_price = float(current[2])
        target = self._select_long_target(entry_price, float(channel.middleband[-1]), float(vwap[-1]))
        if target is None:
            return None

        if not (
            float(adx) <= self.hp['max_adx']
            and float(willr) <= self.hp['willr_long_threshold']
            and float(previous[4]) < float(channel.lowerband[-2])
            and float(previous[2]) < float(channel.lowerband[-2])
            and entry_price > float(channel.lowerband[-1])
            and entry_price > float(current[1])
        ):
            return None

        stop = min(float(previous[4]), float(current[4])) - float(atr) * self.hp['stop_atr_buffer']
        if stop >= entry_price:
            return None

        return FadeSignal(stop, target)

    def _detect_short_setup(self, candles: np.ndarray) -> Optional[FadeSignal]:
        channel = ta.donchian(candles, period=self.hp['donchian_period'], sequential=True)
        adx = ta.adx(candles, period=self.hp['adx_period'])
        willr = ta.willr(candles, period=self.hp['willr_period'])
        atr = ta.atr(candles, period=self.hp['atr_period'])
        vwap = ta.vwap(candles, sequential=True)
        if not self._value_inputs_are_usable(channel, adx, willr, atr, vwap):
            return None

        previous = candles[-2]
        current = candles[-1]
        entry_price = float(current[2])
        target = self._select_short_target(entry_price, float(channel.middleband[-1]), float(vwap[-1]))
        if target is None:
            return None

        if not (
            float(adx) <= self.hp['max_adx']
            and float(willr) >= self.hp['willr_short_threshold']
            and float(previous[3]) > float(channel.upperband[-2])
            and float(previous[2]) > float(channel.upperband[-2])
            and entry_price < float(channel.upperband[-1])
            and entry_price < float(current[1])
        ):
            return None

        stop = max(float(previous[3]), float(current[3])) + float(atr) * self.hp['stop_atr_buffer']
        if stop <= entry_price:
            return None

        return FadeSignal(stop, target)

    def _queue_signal(self, side: str, stop_price: float, target_price: float) -> None:
        entry_price = float(self.price)

        if side == 'long' and (stop_price >= entry_price or target_price <= entry_price):
            return
        if side == 'short' and (stop_price <= entry_price or target_price >= entry_price):
            return

        self.vars['signal_side'] = side
        self.vars['signal_stop'] = stop_price
        self.vars['signal_target'] = target_price

    def _position_qty(self, stop_price: float) -> float:
        precision = self._qty_rounding_precision()
        qty = utils.risk_to_qty(
            self.balance,
            self.hp['risk_per_trade_pct'],
            self.price,
            stop_price,
            precision=precision,
            fee_rate=self.fee_rate,
        )
        min_qty = round(1 / (10 ** precision), precision)
        return max(qty, min_qty)

    def _qty_rounding_precision(self) -> int:
        try:
            return self._qty_precision
        except KeyError:
            return 3

    @staticmethod
    def _value_inputs_are_usable(channel, adx, willr, atr, vwap) -> bool:
        return bool(
            np.isfinite(channel.upperband[-1])
            and np.isfinite(channel.upperband[-2])
            and np.isfinite(channel.middleband[-1])
            and np.isfinite(channel.lowerband[-1])
            and np.isfinite(channel.lowerband[-2])
            and np.isfinite(adx)
            and np.isfinite(willr)
            and np.isfinite(atr)
            and np.isfinite(vwap[-1])
        )

    @staticmethod
    def _select_long_target(entry_price: float, middle: float, vwap: float) -> Optional[float]:
        candidates = [value for value in (middle, vwap) if value > entry_price]
        if not candidates:
            return None
        return min(candidates)

    @staticmethod
    def _select_short_target(entry_price: float, middle: float, vwap: float) -> Optional[float]:
        candidates = [value for value in (middle, vwap) if value < entry_price]
        if not candidates:
            return None
        return max(candidates)
