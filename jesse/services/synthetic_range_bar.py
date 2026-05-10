from typing import List, Optional

import numpy as np

from jesse.services import candle_service


class SyntheticRangeBarBuilder:
    def __init__(self, range_size: float, max_bars: int = 300) -> None:
        if range_size <= 0:
            raise ValueError('range_size must be greater than zero')
        if max_bars < 1:
            raise ValueError('max_bars must be greater than zero')

        self.range_size = float(range_size)
        self.max_bars = int(max_bars)
        self.reset()

    def reset(self) -> None:
        self._completed: List[np.ndarray] = []
        self._forming: Optional[np.ndarray] = None
        self._last_processed_timestamp: Optional[int] = None
        self._processed_count = 0

    @property
    def completed_bars(self) -> np.ndarray:
        if len(self._completed) == 0:
            return np.zeros((0, 6), dtype=np.float64)
        return np.array(self._completed, dtype=np.float64)

    @property
    def forming_bar(self) -> Optional[np.ndarray]:
        if self._forming is None:
            return None
        return self._forming.copy()

    @property
    def last_processed_timestamp(self) -> Optional[int]:
        return self._last_processed_timestamp

    @property
    def processed_count(self) -> int:
        return self._processed_count

    def rebuild(self, candles: np.ndarray) -> None:
        self.reset()
        if candles is None or len(candles) == 0:
            return

        for candle in candles:
            self.update(candle)

    def update(self, candle: np.ndarray) -> List[np.ndarray]:
        candle = np.asarray(candle, dtype=np.float64)
        if candle.shape != (6,):
            raise ValueError('candle must be a numpy array shaped like [timestamp, open, close, high, low, volume]')

        timestamp = int(candle[0])
        if self._last_processed_timestamp == timestamp:
            return []

        if self._forming is None:
            self._forming = self._new_bar(timestamp, float(candle[1]))

        completed: List[np.ndarray] = []
        self._process_candle(candle, completed)

        self._last_processed_timestamp = timestamp
        self._processed_count += 1
        return completed

    def _process_candle(self, candle: np.ndarray, completed: List[np.ndarray]) -> None:
        timestamp = int(candle[0])
        candle_open = float(candle[1])
        candle_volume = float(candle[5])
        current_price = float(self._forming[2])

        if not np.isclose(current_price, candle_open):
            self._process_segment(current_price, candle_open, 0.0, timestamp, completed)

        path = self._price_path(candle)
        distances = [abs(path[i + 1] - path[i]) for i in range(len(path) - 1)]
        moving_segment_indexes = [i for i, distance in enumerate(distances) if distance > 0]

        if len(moving_segment_indexes) == 0:
            self._update_forming(float(path[-1]), candle_volume)
            return

        total_distance = sum(distances)
        remaining_volume = candle_volume
        last_moving_index = moving_segment_indexes[-1]

        for index in moving_segment_indexes:
            start = float(path[index])
            end = float(path[index + 1])

            if index == last_moving_index:
                segment_volume = remaining_volume
            else:
                segment_volume = candle_volume * (distances[index] / total_distance)
                remaining_volume -= segment_volume

            self._process_segment(start, end, segment_volume, timestamp, completed)

    def _process_segment(
        self,
        start: float,
        end: float,
        segment_volume: float,
        timestamp: int,
        completed: List[np.ndarray],
    ) -> None:
        if np.isclose(start, end):
            self._update_forming(end, segment_volume)
            return

        direction = 1.0 if end > start else -1.0
        current_price = float(start)
        remaining_distance = abs(end - start)
        remaining_volume = float(segment_volume)

        while remaining_distance > 1e-12:
            target_price = float(self._forming[1]) + (self.range_size * direction)
            distance_to_target = abs(target_price - current_price)

            if distance_to_target <= remaining_distance + 1e-12:
                used_volume = 0.0
                if remaining_distance > 0:
                    used_volume = remaining_volume * (distance_to_target / remaining_distance)

                self._update_forming(target_price, used_volume)
                completed_bar = self._forming.copy()
                self._append_completed_bar(completed_bar)
                completed.append(completed_bar)

                self._forming = self._new_bar(timestamp, target_price)

                current_price = target_price
                remaining_distance = max(0.0, remaining_distance - distance_to_target)
                remaining_volume = max(0.0, remaining_volume - used_volume)
            else:
                self._update_forming(end, remaining_volume)
                return

        if remaining_volume > 0:
            self._forming[5] += remaining_volume

    def _append_completed_bar(self, bar: np.ndarray) -> None:
        self._completed.append(bar)
        if len(self._completed) > self.max_bars:
            self._completed.pop(0)

    def _update_forming(self, price: float, volume: float) -> None:
        self._forming[2] = price
        self._forming[3] = max(self._forming[3], price)
        self._forming[4] = min(self._forming[4], price)
        self._forming[5] += volume

    @staticmethod
    def _new_bar(timestamp: int, price: float) -> np.ndarray:
        return np.array([timestamp, price, price, price, price, 0.0], dtype=np.float64)

    @staticmethod
    def _price_path(candle: np.ndarray) -> List[float]:
        open_price = float(candle[1])
        close_price = float(candle[2])
        high_price = float(candle[3])
        low_price = float(candle[4])

        # Keep synthetic range bars aligned with Jesse's own intrabar execution assumption.
        if candle_service.is_bullish(candle):
            return [open_price, low_price, high_price, close_price]

        return [open_price, high_price, low_price, close_price]
