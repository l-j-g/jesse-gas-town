import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / 'scripts' / 'run-wave1-original-refinement-matrix.py'
spec = importlib.util.spec_from_file_location('wave1_original_refinement_matrix', SCRIPT_PATH)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def test_default_pairs_cover_originals_and_refinements():
    assert runner.DEFAULT_PAIRS == [
        ('KAMA_TrendFollowing', 'KamaPullbackReclaim', '15m'),
        ('SuperScalper', 'SuperScalperTimeStopScratch', '15m'),
        ('TrendWaveRiderV2', 'TrendWaveRiderV2ShallowPullbackBand', '15m'),
        ('TurtleV2', 'TurtleV2FailedBreakTimeStop', '1h'),
    ]


def test_default_data_timeframes_cover_private_htf_refs():
    assert runner.DEFAULT_DATA_TIMEFRAMES == ('4h', '6h')


def test_filter_pairs_matches_original_or_refinement_name():
    assert runner.filter_pairs(runner.DEFAULT_PAIRS, 'TrendWaveRiderV2') == [
        ('TrendWaveRiderV2', 'TrendWaveRiderV2ShallowPullbackBand', '15m')
    ]
    assert runner.filter_pairs(runner.DEFAULT_PAIRS, 'TrendWaveRiderV2ShallowPullbackBand') == [
        ('TrendWaveRiderV2', 'TrendWaveRiderV2ShallowPullbackBand', '15m')
    ]


def test_filter_pairs_rejects_unknown_name():
    try:
        runner.filter_pairs(runner.DEFAULT_PAIRS, 'NoSuchStrategy')
    except ValueError as exc:
        assert 'matched no pairs' in str(exc)
    else:
        raise AssertionError('expected ValueError')


def test_parse_extra_pairs_accepts_original_refinement_timeframe():
    assert runner.parse_extra_pairs('A:B:1h,C:D:15m') == [
        ('A', 'B', '1h'),
        ('C', 'D', '15m'),
    ]


def test_parse_extra_pairs_rejects_bad_shape():
    try:
        runner.parse_extra_pairs('A:B')
    except ValueError as exc:
        assert 'original:refinement:timeframe' in str(exc)
    else:
        raise AssertionError('expected ValueError')


def test_profit_factor_handles_zero_loss():
    assert runner.profit_factor({'gross_profit': 10, 'gross_loss': 0}) is None
    assert runner.profit_factor({'gross_profit': 10, 'gross_loss': -5}) == 2


def test_decision_uses_percent_drawdown_units():
    assert runner.decision({
        'total': 20,
        'expectancy': 1,
        'net_profit_percentage': 5,
        'max_drawdown': -5,
    }) == 'revise: positive slice, needs route robustness'
    assert runner.decision({
        'total': 20,
        'expectancy': 1,
        'net_profit_percentage': 5,
        'max_drawdown': -25,
    }) == 'revise: positive but drawdown too high'


def test_comparison_rows_compute_deltas():
    rows = [
        {
            'status': 'ok',
            'strategy': 'A',
            'symbol': 'BTC-USDT',
            'timeframe': '1h',
            'net_profit_percentage': 1,
            'expectancy': 2,
            'max_drawdown': -3,
            'total': 4,
            'decision': 'base',
        },
        {
            'status': 'ok',
            'strategy': 'B',
            'symbol': 'BTC-USDT',
            'timeframe': '1h',
            'net_profit_percentage': 1.5,
            'expectancy': 1,
            'max_drawdown': -2,
            'total': 6,
            'decision': 'variant',
        },
    ]

    comparisons = runner.comparison_rows(rows, [('A', 'B', '1h')])

    assert comparisons == [
        {
            'symbol': 'BTC-USDT',
            'timeframe': '1h',
            'original': 'A',
            'refinement': 'B',
            'net_profit_percentage_delta': 0.5,
            'expectancy_delta': -1,
            'max_drawdown_delta': 1,
            'trade_count_delta': 2,
            'original_decision': 'base',
            'refinement_decision': 'variant',
        }
    ]


def test_process_error_row_records_child_failure():
    row = runner.process_error_row(
        'Binance Perpetual Futures',
        'BTC-USDT',
        'SuperScalper',
        '15m',
        '2024-01-01',
        '2024-01-08',
        0.0004,
        3,
        -6,
        'Fatal Python error: Aborted\ntrace',
    )

    assert row['status'] == 'error'
    assert row['decision'] == 'blocked: runtime error'
    assert 'returncode -6' in row['error']
    assert 'Fatal Python error: Aborted' in row['error']
