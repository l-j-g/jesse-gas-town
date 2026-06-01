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
    {
        'base_class': 'KAMA_TrendFollowing',
        'variant': 'KAMA Pullback Reclaim',
        'changed_component': 'entry trigger',
        'implementation_status': 'docs_only_not_generated',
    },
    {
        'base_class': 'SuperScalper',
        'variant': 'SuperScalper Time-Stop Scratch',
        'changed_component': 'trade management',
        'implementation_status': 'docs_only_not_generated',
    },
    {
        'base_class': 'TrendWaveRiderV2',
        'variant': 'TrendWaveRiderV2 Shallow Pullback Band',
        'changed_component': 'entry trigger',
        'implementation_status': 'docs_only_not_generated',
    },
    {
        'base_class': 'TurtleV2',
        'variant': 'Turtle V2 Failed-Break Time Stop',
        'changed_component': 'trade management',
        'implementation_status': 'docs_only_not_generated',
    },
)


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
    dst.write_text(extract_strategy_code(src), encoding='utf-8')
    return {
        **asdict(strategy),
        'source_path': str(src),
        'target_module': f"strategies.{strategy.class_name}",
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
    manifest = {
        'source_policy': 'private Jesse.Trade source is copied only into gitignored .runtime',
        'runtime_root': str(runtime_root),
        'originals': originals,
        'refinements': REFINEMENT_QUEUE,
    }
    manifest_path = runtime_root / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8')

    if args.check_imports:
        check_imports(runtime_root, originals)

    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
