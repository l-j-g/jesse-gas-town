from collections import namedtuple
from typing import Optional

import numpy as np

import jesse.indicators as ta
import jesse.utils as utils
from jesse.strategies.Strategy import Strategy


PullbackSignal = namedtuple('PullbackSignal', ['stop', 'target'])


class KamaAdxPullback(Strategy):
    def __init__(self) -> None:
        super().__init__()
        self.vars['signal_side'] = None
        self.vars['signal_stop'] = None
        self.vars['signal_target'] = None

    def hyperparameters(self):
        return [
            {'name': 'kama_period', 'type': int, 'min': 10, 'max': 55, 'default': 21},
            {'name': 'kama_fast_length', 'type': int, 'min': 2, 'max': 6, 'default': 2},
            {'name': 'kama_slow_length', 'type': int, 'min': 20, 'max': 60, 'default': 30},
            {'name': 'adx_period', 'type': int, 'min': 7, 'max': 28, 'default': 14},
            {'name': 'adx_threshold', 'type': float, 'min': 15.0, 'max': 40.0, 'default': 22.0},
            {'name': 'pullback_lookback', 'type': int, 'min': 2, 'max': 6, 'default': 3},
            {'name': 'atr_period', 'type': int, 'min': 7, 'max': 28, 'default': 14},
            {'name': 'atr_stop_mult', 'type': float, 'min': 0.5, 'max': 3.0, 'default': 1.2},
            {'name': 'risk_per_trade_pct', 'type': float, 'min': 0.1, 'max': 2.0, 'default': 0.5},
            {'name': 'take_profit_r', 'type': float, 'min': 1.0, 'max': 5.0, 'default': 2.2},
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
            self.hp['kama_period'],
            self.hp['adx_period'] * 2,
            self.hp['atr_period'],
        ) + self.hp['pullback_lookback'] + 2
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

    def _detect_long_setup(self, candles: np.ndarray) -> Optional[PullbackSignal]:
        kama = ta.kama(
            candles,
            period=self.hp['kama_period'],
            fast_length=self.hp['kama_fast_length'],
            slow_length=self.hp['kama_slow_length'],
            sequential=True,
        )
        di = ta.di(candles, period=self.hp['adx_period'], sequential=True)
        adx = ta.adx(candles, period=self.hp['adx_period'])
        atr = ta.atr(candles, period=self.hp['atr_period'])
        if not self._trend_inputs_are_usable(kama, di.plus, di.minus, adx, atr):
            return None

        current = candles[-1]
        previous = candles[-2]
        recent = candles[-(self.hp['pullback_lookback'] + 1):-1]
        recent_kama = kama[-(self.hp['pullback_lookback'] + 1):-1]
        current_close = float(current[2])

        if not (
            current_close > float(kama[-1])
            and float(kama[-1]) > float(kama[-2])
            and float(di.plus[-1]) > float(di.minus[-1])
            and float(adx) >= self.hp['adx_threshold']
            and np.any(recent[:, 4] <= recent_kama)
            and current_close > float(current[1])
            and current_close > float(previous[3])
        ):
            return None

        stop = float(recent[:, 4].min()) - float(atr) * self.hp['atr_stop_mult']
        if stop >= current_close:
            return None

        target = current_close + (current_close - stop) * self.hp['take_profit_r']
        return PullbackSignal(stop, target)

    def _detect_short_setup(self, candles: np.ndarray) -> Optional[PullbackSignal]:
        kama = ta.kama(
            candles,
            period=self.hp['kama_period'],
            fast_length=self.hp['kama_fast_length'],
            slow_length=self.hp['kama_slow_length'],
            sequential=True,
        )
        di = ta.di(candles, period=self.hp['adx_period'], sequential=True)
        adx = ta.adx(candles, period=self.hp['adx_period'])
        atr = ta.atr(candles, period=self.hp['atr_period'])
        if not self._trend_inputs_are_usable(kama, di.plus, di.minus, adx, atr):
            return None

        current = candles[-1]
        previous = candles[-2]
        recent = candles[-(self.hp['pullback_lookback'] + 1):-1]
        recent_kama = kama[-(self.hp['pullback_lookback'] + 1):-1]
        current_close = float(current[2])

        if not (
            current_close < float(kama[-1])
            and float(kama[-1]) < float(kama[-2])
            and float(di.minus[-1]) > float(di.plus[-1])
            and float(adx) >= self.hp['adx_threshold']
            and np.any(recent[:, 3] >= recent_kama)
            and current_close < float(current[1])
            and current_close < float(previous[4])
        ):
            return None

        stop = float(recent[:, 3].max()) + float(atr) * self.hp['atr_stop_mult']
        if stop <= current_close:
            return None

        target = current_close - (stop - current_close) * self.hp['take_profit_r']
        return PullbackSignal(stop, target)

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
    def _trend_inputs_are_usable(kama, plus_di, minus_di, adx, atr) -> bool:
        return bool(
            len(kama) >= 2
            and np.isfinite(kama[-1])
            and np.isfinite(kama[-2])
            and np.isfinite(plus_di[-1])
            and np.isfinite(minus_di[-1])
            and np.isfinite(adx)
            and np.isfinite(atr)
        )
