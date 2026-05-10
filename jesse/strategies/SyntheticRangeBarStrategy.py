from abc import abstractmethod
from typing import Optional

import numpy as np

from jesse import exceptions
from jesse.services.synthetic_range_bar import SyntheticRangeBarBuilder
from jesse.strategies.Strategy import Strategy


class SyntheticRangeBarStrategy(Strategy):
    """
    Strategy helper for building synthetic range bars from Jesse's native 1m candles.

    Keep the route timeframe on 1m for per-minute updates. Strategy signals can then
    use synthetic range bars without changing the engine's storage or execution model.
    """

    def __init__(self) -> None:
        super().__init__()
        self._synthetic_range_builder: Optional[SyntheticRangeBarBuilder] = None
        self._synthetic_range_signature: Optional[tuple[float, int]] = None

    @abstractmethod
    def synthetic_range_bar_size(self) -> float:
        pass

    def synthetic_range_max_bars(self) -> int:
        return 300

    @property
    def synthetic_range_bars(self) -> np.ndarray:
        if self._synthetic_range_builder is None:
            return np.zeros((0, 6), dtype=np.float64)
        return self._synthetic_range_builder.completed_bars

    @property
    def forming_synthetic_range_bar(self) -> Optional[np.ndarray]:
        if self._synthetic_range_builder is None:
            return None
        return self._synthetic_range_builder.forming_bar

    @property
    def synthetic_range_last_processed_1m(self) -> Optional[int]:
        if self._synthetic_range_builder is None:
            return None
        return self._synthetic_range_builder.last_processed_timestamp

    @property
    def synthetic_range_processed_count(self) -> int:
        if self._synthetic_range_builder is None:
            return 0
        return self._synthetic_range_builder.processed_count

    def before(self) -> None:
        self._sync_synthetic_range_bars()

    def _sync_synthetic_range_bars(self) -> None:
        if self.timeframe != '1m':
            raise exceptions.InvalidStrategy(
                'SyntheticRangeBarStrategy requires a 1m route timeframe so synthetic bars update every minute.'
            )

        signature = (float(self.synthetic_range_bar_size()), int(self.synthetic_range_max_bars()))

        if signature[0] <= 0:
            raise exceptions.InvalidStrategy('synthetic_range_bar_size() must return a value greater than zero.')

        if self._synthetic_range_builder is None or self._synthetic_range_signature != signature:
            self._synthetic_range_builder = SyntheticRangeBarBuilder(*signature)
            self._synthetic_range_signature = signature
            self._synthetic_range_builder.rebuild(self.get_candles(self.exchange, self.symbol, '1m'))
            return

        candles_1m = self.get_candles(self.exchange, self.symbol, '1m')
        if len(candles_1m) == 0:
            return

        self._synthetic_range_builder.update(candles_1m[-1])
