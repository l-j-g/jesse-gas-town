from jesse.strategies import SyntheticRangeBarStrategy


class TestSyntheticRangeBarStrategy(SyntheticRangeBarStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.vars['entry_count'] = 0

    def synthetic_range_bar_size(self) -> float:
        return 10

    def should_long(self):
        if self.position.is_open or self.trades_count > 0:
            return False

        bars = self.synthetic_range_bars
        return len(bars) >= 2 and bars[-1][2] > bars[-2][2]

    def go_long(self):
        self.vars['entry_count'] += 1
        self.buy = 1, self.price
        self.stop_loss = 1, self.price - 5
        self.take_profit = 1, self.price + 1

    def should_cancel_entry(self):
        return False
