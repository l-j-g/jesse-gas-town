import numpy as np

import jesse.indicators as ta
import jesse.utils as utils
from jesse.strategies import Strategy


class BaselineMaTrend(Strategy):
    """Simple 1h moving-average trend baseline for research workflow validation."""

    def __init__(self) -> None:
        super().__init__()
        self.vars['signal_side'] = None
        self.vars['signal_stop'] = None
        self.vars['signal_target'] = None
        self.vars['active_stop'] = None

    def hyperparameters(self):
        return [
            {'name': 'fast_ma', 'type': int, 'min': 10, 'max': 30, 'default': 20},
            {'name': 'slow_ma', 'type': int, 'min': 30, 'max': 80, 'default': 50},
            {'name': 'trend_ma', 'type': int, 'min': 100, 'max': 250, 'default': 100},
            {'name': 'atr_period', 'type': int, 'min': 10, 'max': 30, 'default': 14},
            {'name': 'atr_stop', 'type': float, 'min': 1.0, 'max': 4.0, 'default': 2.0},
            {'name': 'reward_risk', 'type': float, 'min': 1.0, 'max': 4.0, 'default': 2.0},
            {'name': 'risk_per_trade', 'type': float, 'min': 0.0025, 'max': 0.02, 'default': 0.005},
            {'name': 'max_notional_pct', 'type': float, 'min': 0.05, 'max': 0.50, 'default': 0.20},
        ]

    def should_long(self) -> bool:
        return self.vars['signal_side'] == 'long'

    def should_short(self) -> bool:
        return self.vars['signal_side'] == 'short'

    def should_cancel_entry(self) -> bool:
        return False

    def before(self) -> None:
        if self.position.is_open:
            return

        self._clear_signal()

        if len(self.candles) < self.hp['trend_ma'] + 2:
            return

        fast = ta.sma(self.candles, self.hp['fast_ma'], sequential=True)
        slow = ta.sma(self.candles, self.hp['slow_ma'], sequential=True)
        trend = ta.sma(self.candles, self.hp['trend_ma'], sequential=True)
        atr = ta.atr(self.candles, self.hp['atr_period'])

        if not self._finite(fast[-2], fast[-1], slow[-2], slow[-1], trend[-1], atr):
            return

        price = float(self.price)
        crossed_up = fast[-2] <= slow[-2] and fast[-1] > slow[-1]
        crossed_down = fast[-2] >= slow[-2] and fast[-1] < slow[-1]

        if crossed_up and price > trend[-1] and fast[-1] > trend[-1]:
            stop = price - (float(atr) * self.hp['atr_stop'])
            self._set_signal('long', price, stop)
        elif crossed_down and price < trend[-1] and fast[-1] < trend[-1]:
            stop = price + (float(atr) * self.hp['atr_stop'])
            self._set_signal('short', price, stop)

    def go_long(self) -> None:
        qty = self._entry_qty(float(self.price), float(self.vars['signal_stop']))
        self.buy = qty, self.price
        self.stop_loss = qty, self.vars['signal_stop']
        self.take_profit = qty, self.vars['signal_target']
        self.vars['active_stop'] = self.vars['signal_stop']
        self.vars['signal_side'] = None

    def go_short(self) -> None:
        qty = self._entry_qty(float(self.price), float(self.vars['signal_stop']))
        self.sell = qty, self.price
        self.stop_loss = qty, self.vars['signal_stop']
        self.take_profit = qty, self.vars['signal_target']
        self.vars['active_stop'] = self.vars['signal_stop']
        self.vars['signal_side'] = None

    def update_position(self) -> None:
        fast = ta.sma(self.candles, self.hp['fast_ma'])

        if not np.isfinite(fast):
            return

        if self.vars['active_stop'] is None:
            return

        if self.is_long and fast < self.price and fast > self.vars['active_stop']:
            self.vars['active_stop'] = float(fast)
            self.stop_loss = self.position.qty, float(fast)
        elif self.is_short and fast > self.price and fast < self.vars['active_stop']:
            self.vars['active_stop'] = float(fast)
            self.stop_loss = self.position.qty, float(fast)

    def on_close_position(self, order, closed_trade) -> None:
        self._clear_signal()
        self.vars['active_stop'] = None

    def _set_signal(self, side: str, entry: float, stop: float) -> None:
        risk = abs(entry - stop)
        if risk <= 0:
            return

        target = entry + risk * self.hp['reward_risk'] if side == 'long' else entry - risk * self.hp['reward_risk']
        self.vars['signal_side'] = side
        self.vars['signal_stop'] = stop
        self.vars['signal_target'] = target

    def _entry_qty(self, entry: float, stop: float) -> float:
        risk_qty = utils.risk_to_qty(
            self.balance,
            self.hp['risk_per_trade'],
            entry,
            stop,
            precision=6,
            fee_rate=0,
        )
        max_qty = utils.size_to_qty(
            self.balance * self.hp['max_notional_pct'] * self.leverage,
            entry,
            precision=6,
            fee_rate=0,
        )
        return max(0.0, min(risk_qty, max_qty))

    def _clear_signal(self) -> None:
        self.vars['signal_side'] = None
        self.vars['signal_stop'] = None
        self.vars['signal_target'] = None

    @staticmethod
    def _finite(*values: float) -> bool:
        return all(np.isfinite(v) for v in values)
