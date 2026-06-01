import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / 'scripts' / 'prepare-wave1-private-strategies.py'
spec = importlib.util.spec_from_file_location('prepare_wave1_private_strategies', SCRIPT_PATH)
prep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prep)


def test_wave1_manifest_tracks_originals_and_refinement_queue():
    assert [s.class_name for s in prep.WAVE1_ORIGINALS] == [
        'KAMA_TrendFollowing',
        'SuperScalper',
        'TrendWaveRiderV2',
        'TurtleV2',
    ]

    assert [r.variant for r in prep.REFINEMENT_QUEUE] == [
        'KAMA Pullback Reclaim',
        'SuperScalper Time-Stop Scratch',
        'TrendWaveRiderV2 Shallow Pullback Band',
        'Turtle V2 Failed-Break Time Stop',
    ]

    assert [r.class_name for r in prep.REFINEMENT_QUEUE] == [
        'KamaPullbackReclaim',
        'SuperScalperTimeStopScratch',
        'TrendWaveRiderV2ShallowPullbackBand',
        'TurtleV2FailedBreakTimeStop',
    ]


def test_prepare_strategy_missing_private_source_is_non_fatal(tmp_path):
    strategy = prep.WAVE1_ORIGINALS[0]
    row = prep.prepare_strategy(tmp_path / 'missing-source', tmp_path / 'runtime', strategy)

    assert row['class_name'] == 'KAMA_TrendFollowing'
    assert row['prepared'] is False
    assert row['reason'] == 'missing_private_source'


def test_prepare_refinement_missing_base_is_non_fatal(tmp_path):
    row = prep.prepare_refinement(tmp_path / 'runtime', prep.REFINEMENT_QUEUE[0], set())

    assert row['class_name'] == 'KamaPullbackReclaim'
    assert row['prepared'] is False
    assert row['reason'] == 'missing_prepared_base_class'
