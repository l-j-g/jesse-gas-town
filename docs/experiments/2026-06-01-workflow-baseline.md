# Experiment: Workflow Baseline

Date: 2026-06-01
Status: complete
Decision: keep as workflow baseline, refine only after more evidence

## Hypothesis

A minimal 1h moving-average trend-following baseline can act as the control strategy for later MA crossover, three-MA, multi-timeframe, regime-filter, and conviction-allocation experiments.

## Simplest Testable Version

Implemented `BaselineMaTrend` with:
- 1h `Binance Perpetual Futures` / `BTC-USDT` route for real imported candles
- 1h `Sandbox` / `BTC-USDT` synthetic runner for smoke validation
- 20/50/100 SMA trend and crossover model
- ATR stop, fixed R-multiple target, 1x futures assumptions
- risk-based size capped by notional percentage
- no live exchange keys or live execution setup

## Config

- Strategy: `BaselineMaTrend`
- Exchange: `Binance Perpetual Futures`
- Symbol: `BTC-USDT`
- Timeframe: `1h`
- Date range: `2024-01-01` to `2024-06-01`
- Fee model: `0.0004`
- Slippage assumption: none
- Leverage: `1x`
- Position sizing: `0.5%` risk cap, `20%` notional cap
- Data: imported Jesse DB 1m candles

## Exact Commands

Focused smoke test:
```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Users/lg/src/jesse/.venv/bin/python -m pytest tests/test_baseline_ma_trend.py
```

Synthetic local backtest:
```bash
/Users/lg/src/jesse/.venv/bin/python scripts/run-baseline-ma-trend-backtest.py
```

Real imported-candle backtest:
```bash
/Users/lg/src/jesse/.venv/bin/python scripts/run-baseline-ma-trend-db-backtest.py --start 2024-01-01 --finish 2024-06-01
```

Small public candle import through Jesse:
```bash
/Users/lg/src/jesse/.venv/bin/python scripts/import-btc-usdt-candles.py --exchange "Bybit USDT Perpetual" --symbol BTC-USDT --start 2026-05-25
```

Runtime check:
```bash
/Users/lg/src/jesse/.venv/bin/jesse run
curl -fsS http://127.0.0.1:9000/
curl -fsS http://localhost:9002/mcp
```

## Metrics

Synthetic local run:
- net profit: `-6.5896437572922295`
- net profit percentage: `-0.0658964375729223`
- annual return: `-0.26697773406857417`
- max drawdown: `-0.06589643757292096`
- Sharpe: `-6.331145124113147`
- Sortino: `-6.073525778206324`
- Calmar: `-4.051474463595042`
- total trades: `9`
- win rate: `0.0`
- longs: `9`
- shorts: `0`
- expectancy: `-0.7321826396991367`
- fees: `3.125183140973581`

Real imported BTC-USDT run, Binance Perpetual Futures, `2024-01-01` to `2024-06-01`:
- net profit: `2.332342600554372`
- net profit percentage: `0.023323426005543723`
- annual return: `0.05601606392253711`
- max drawdown: `-0.019072301301470418`
- Sharpe: `1.1541418197151636`
- Sortino: `2.2266690677972223`
- Calmar: `2.9370374889273814`
- total trades: `33`
- win rate: `0.42424242424242425`
- longs: `17`
- shorts: `16`
- expectancy: `0.07067704850164763`
- profit factor proxy: `gross_profit / abs(gross_loss) = 1.3829`
- fees: `0.8719307979921519`
- open trades at finish: `1`

## Results

The baseline ran end-to-end through Jesse's research backtest path on both synthetic candles and real imported candles. The real BTC-USDT slice was slightly positive, but the evidence is weak: only 33 trades, no slippage model, one market, one date range, and one open trade at the end.

## Risks And Failure Modes

- Synthetic candles are not market data; they only verify mechanics.
- 33 real trades is still too few for robust strategy quality conclusions.
- Profit is tiny relative to the evaluation scope; fees/slippage could erase it.
- One BTC-USDT slice says little about ETH, other regimes, or out-of-sample behavior.
- Short side underperformed long side by win rate and needs separate review.
- One open trade remains at the end, so final-period exposure must be reviewed.
- Moving-average systems are regime dependent and can be damaged by chop, fees, and late exits.
- Jesse app runtime works on `9000`, but MCP on `9002` is not exposed by the current local runtime.

## One Refinement

Run the unchanged baseline across a wider route matrix: BTC-USDT and ETH-USDT, at least one uptrend slice, one downtrend slice, and one choppy slice. Do not optimize parameters until that matrix is logged.

## Evidence

- Gas Town epic: `jt-cin`
- Setup/backtest task: `jt-cin.11`
- Route: `routes.py`
- Strategy: `strategies/BaselineMaTrend/__init__.py`
- Runner: `scripts/run-baseline-ma-trend-backtest.py`
- DB runner: `scripts/run-baseline-ma-trend-db-backtest.py`
- Import helper: `scripts/import-btc-usdt-candles.py`
- Smoke test: `tests/test_baseline_ma_trend.py`
