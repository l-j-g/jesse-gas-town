#!/usr/bin/env python
"""Prepare private Wave 1 Jesse.Trade strategies for local-only backtests.

Account-downloaded strategy source stays gitignored under
references/jesse-trade-strategies/source. This script copies selected strategy
files into .runtime so tests/backtests can import them without committing
private source.
"""

import argparse
import importlib
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_ROOT = ROOT / 'references' / 'jesse-trade-strategies' / 'source'
DEFAULT_RUNTIME_ROOT = ROOT / '.runtime' / 'wave1-private-strategies'


@dataclass(frozen=True)
class Wave1Strategy:
    slug: str
    class_name: str
    family: str
    baseline_timeframes: tuple[str, ...]
    baseline_symbols: tuple[str, ...] = ('BTC-USDT', 'ETH-USDT', 'SOL-USDT')
    implementation_status: str = 'private_source_required'


@dataclass(frozen=True)
class Wave1Refinement:
    base_class: str
    class_name: str
    variant: str
    changed_component: str
    thesis: str
    implementation_status: str = 'generated_local_only'


WAVE1_ORIGINALS = (
    Wave1Strategy(
        slug='kama-trendfollowing',
        class_name='KAMA_TrendFollowing',
        family='trend continuation',
        baseline_timeframes=('15m', '30m', '1h'),
    ),
    Wave1Strategy(
        slug='superscalper',
        class_name='SuperScalper',
        family='trend-aligned scalper',
        baseline_timeframes=('5m', '15m', '30m'),
    ),
    Wave1Strategy(
        slug='trendwaveriderv2',
        class_name='TrendWaveRiderV2',
        family='trend pullback',
        baseline_timeframes=('15m', '30m', '1h'),
    ),
    Wave1Strategy(
        slug='turtle-v2',
        class_name='TurtleV2',
        family='donchian breakout',
        baseline_timeframes=('30m', '1h', '2h'),
    ),
)


REFINEMENT_QUEUE = (
    Wave1Refinement(
        base_class='KAMA_TrendFollowing',
        class_name='KamaPullbackReclaim',
        variant='KAMA Pullback Reclaim',
        changed_component='entry trigger',
        thesis='Require a KAMA touch-and-reclaim before taking the base continuation signal.',
    ),
    Wave1Refinement(
        base_class='SuperScalper',
        class_name='SuperScalperTimeStopScratch',
        variant='SuperScalper Time-Stop Scratch',
        changed_component='trade management',
        thesis='Scratch stalled scalps after a short bar window if price has not moved in favor.',
    ),
    Wave1Refinement(
        base_class='TrendWaveRiderV2',
        class_name='TrendWaveRiderV2ShallowPullbackBand',
        variant='TrendWaveRiderV2 Shallow Pullback Band',
        changed_component='entry trigger',
        thesis='Allow shallower CCI pullback resets while keeping the base trend gates.',
    ),
    Wave1Refinement(
        base_class='TurtleV2',
        class_name='TurtleV2FailedBreakTimeStop',
        variant='Turtle V2 Failed-Break Time Stop',
        changed_component='trade management',
        thesis='Cut breakouts that fail to show directional follow-through within a few bars.',
    ),
)


REFINEMENT_SOURCES = {
    'KamaPullbackReclaim': '''from strategies.KAMA_TrendFollowing import KAMA_TrendFollowing


class KamaPullbackReclaim(KAMA_TrendFollowing):
    """KAMA continuation variant: require pullback touch then reclaim."""

    def should_long(self) -> bool:
        return super().should_long() and self._reclaimed_kama_long()

    def should_short(self) -> bool:
        return super().should_short() and self._reclaimed_kama_short()

    def _reclaimed_kama_long(self) -> bool:
        kama = float(self.kama)
        return float(self.candles[-1, 4]) <= kama < float(self.price)

    def _reclaimed_kama_short(self) -> bool:
        kama = float(self.kama)
        return float(self.candles[-1, 3]) >= kama > float(self.price)
''',
    'SuperScalperTimeStopScratch': '''from strategies.SuperScalper import SuperScalper


class SuperScalperTimeStopScratch(SuperScalper):
    """Scalper variant: scratch stagnant positions after a short bar window."""

    def hyperparameters(self) -> list:
        return super().hyperparameters() + [
            {'name': 'scratch_bars', 'type': int, 'min': 2, 'max': 8, 'default': 4},
        ]

    def on_open_position(self, order) -> None:
        super().on_open_position(order)
        self.vars['opened_index'] = self.index

    def update_position(self) -> None:
        opened_index = self.vars.get('opened_index')
        if opened_index is None or not self.position.is_open:
            return
        if self.index - opened_index < self.hp.get('scratch_bars', 4):
            return
        entry = float(self.position.entry_price)
        if self.is_long and float(self.price) <= entry:
            self.liquidate()
        elif self.is_short and float(self.price) >= entry:
            self.liquidate()
''',
    'TrendWaveRiderV2ShallowPullbackBand': '''from strategies.TrendWaveRiderV2 import TrendWaveRiderV2


class TrendWaveRiderV2ShallowPullbackBand(TrendWaveRiderV2):
    """TrendWaveRiderV2 variant: accept shallower CCI pullback resets."""

    @property
    def oscillator_signal(self):
        if self.cci < -75:
            return 1
        if self.cci > 75:
            return -1
        return 0
''',
    'TurtleV2FailedBreakTimeStop': '''from strategies.TurtleV2 import TurtleV2


class TurtleV2FailedBreakTimeStop(TurtleV2):
    """Turtle V2 variant: time-stop breakouts with no follow-through."""

    def hyperparameters(self) -> list:
        return super().hyperparameters() + [
            {'name': 'failed_break_bars', 'type': int, 'min': 2, 'max': 8, 'default': 4},
        ]

    def on_open_position(self, order) -> None:
        super().on_open_position(order)
        self.vars['opened_index'] = self.index

    def update_position(self) -> None:
        super().update_position()
        opened_index = self.vars.get('opened_index')
        if opened_index is None or not self.position.is_open:
            return
        if self.index - opened_index < self.hp.get('failed_break_bars', 4):
            return
        entry = float(self.position.entry_price)
        if self.is_long and float(self.price) <= entry:
            self.liquidate()
        elif self.is_short and float(self.price) >= entry:
            self.liquidate()
''',
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument('--runtime-root', type=Path, default=DEFAULT_RUNTIME_ROOT)
    parser.add_argument('--check-imports', action='store_true')
    return parser.parse_args()


def source_path(source_root: Path, strategy: Wave1Strategy) -> Path:
    return source_root / strategy.slug / 'Strategy.py'


def target_path(runtime_root: Path, strategy: Wave1Strategy) -> Path:
    return runtime_root / 'strategies' / strategy.class_name / '__init__.py'


def refinement_target_path(runtime_root: Path, refinement: Wave1Refinement) -> Path:
    return runtime_root / 'strategies' / refinement.class_name / '__init__.py'


def extract_strategy_code(src: Path) -> str:
    text = src.read_text(encoding='utf-8')
    stripped = text.lstrip()
    if stripped.startswith('from ') or stripped.startswith('import ') or stripped.startswith('class '):
        return text

    payload = json.JSONDecoder(strict=False).decode(text)
    for item in payload:
        if isinstance(item, dict) and isinstance(item.get('code'), str):
            return item['code']
        if isinstance(item, str) and 'class ' in item and 'Strategy' in item:
            if item.lstrip().startswith(('from ', 'import ', 'class ')):
                return item

    raise ValueError(f'could not find strategy code in {src}')


def normalize_strategy_code(code: str) -> str:
    return (
        code
        .replace('def on_close_position(self, order) -> None:', 'def on_close_position(self, order, closed_trade=None) -> None:')
        .replace('def on_close_position(self, order):', 'def on_close_position(self, order, closed_trade=None):')
        .replace(
            't = ta.supertrend(self.candles)',
            'if len(self.candles) < 10:\n            return 0\n        t = ta.supertrend(self.candles)',
        )
        .replace(
            't = ta.supertrend(self.long_term_candles)',
            'if len(self.long_term_candles) < 10:\n            return 0\n        t = ta.supertrend(self.long_term_candles)',
        )
    )


def prepare_strategy(source_root: Path, runtime_root: Path, strategy: Wave1Strategy) -> dict:
    src = source_path(source_root, strategy)
    if not src.exists():
        return {
            **asdict(strategy),
            'source_path': str(src),
            'target_module': None,
            'prepared': False,
            'reason': 'missing_private_source',
        }

    dst = target_path(runtime_root, strategy)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(normalize_strategy_code(extract_strategy_code(src)), encoding='utf-8')
    return {
        **asdict(strategy),
        'source_path': str(src),
        'target_module': f"strategies.{strategy.class_name}",
        'target_path': str(dst),
        'prepared': True,
    }


def prepare_refinement(runtime_root: Path, refinement: Wave1Refinement, prepared_originals: set[str]) -> dict:
    if refinement.base_class not in prepared_originals:
        return {
            **asdict(refinement),
            'target_module': None,
            'prepared': False,
            'reason': 'missing_prepared_base_class',
        }

    dst = refinement_target_path(runtime_root, refinement)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(REFINEMENT_SOURCES[refinement.class_name], encoding='utf-8')
    return {
        **asdict(refinement),
        'target_module': f"strategies.{refinement.class_name}",
        'target_path': str(dst),
        'prepared': True,
    }


def write_package_init(runtime_root: Path) -> None:
    strategies_root = runtime_root / 'strategies'
    strategies_root.mkdir(parents=True, exist_ok=True)
    (strategies_root / '__init__.py').write_text('', encoding='utf-8')


def check_imports(runtime_root: Path, rows: list[dict]) -> None:
    sys.path.insert(0, str(runtime_root))
    for row in rows:
        if not row.get('prepared'):
            continue
        module = importlib.import_module(row['target_module'])
        if not hasattr(module, row['class_name']):
            raise RuntimeError(f"{row['target_module']} missing {row['class_name']}")


def main() -> None:
    args = parse_args()
    source_root = args.source_root.resolve()
    runtime_root = args.runtime_root.resolve()
    runtime_root.mkdir(parents=True, exist_ok=True)
    write_package_init(runtime_root)

    originals = [prepare_strategy(source_root, runtime_root, s) for s in WAVE1_ORIGINALS]
    prepared_originals = {row['class_name'] for row in originals if row.get('prepared')}
    refinements = [
        prepare_refinement(runtime_root, refinement, prepared_originals)
        for refinement in REFINEMENT_QUEUE
    ]
    manifest = {
        'source_policy': 'private Jesse.Trade source is copied only into gitignored .runtime',
        'runtime_root': str(runtime_root),
        'originals': originals,
        'refinements': refinements,
    }
    manifest_path = runtime_root / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8')

    if args.check_imports:
        check_imports(runtime_root, originals)
        check_imports(runtime_root, refinements)

    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
