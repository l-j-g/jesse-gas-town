# Backtest Summary: BaselineMaTrend BTC-USDT 1h

Date: 2026-06-01
Strategy: `BaselineMaTrend`
Exchange: `Binance Perpetual Futures`
Symbol: `BTC-USDT`
Timeframe: `1h`
Date range: `2024-01-01` to `2024-06-01`

## Command

```bash
/Users/lg/src/jesse/.venv/bin/python scripts/run-baseline-ma-trend-db-backtest.py --start 2024-01-01 --finish 2024-06-01
```

## Config

- starting balance: `10000`
- fee: `0.0004`
- exchange type: futures
- leverage: `1`
- leverage mode: cross
- data source: Jesse DB candles already present locally
- strategy sizing: `0.5%` risk cap and `20%` notional cap

## Metrics

- net profit: `2.332342600554372`
- net profit percentage: `0.023323426005543723`
- annual return: `0.05601606392253711`
- max drawdown: `-0.019072301301470418`
- Sharpe: `1.1541418197151636`
- Sortino: `2.2266690677972223`
- Calmar: `2.9370374889273814`
- total trades: `33`
- win rate: `0.42424242424242425`
- expectancy: `0.07067704850164763`
- gross profit: `8.43708307088589`
- gross loss: `-6.104740470331519`
- fees: `0.8719307979921519`
- longs: `17`
- shorts: `16`
- open trades at finish: `1`

## Review

This run proves the local workflow can use imported Jesse DB candles and produce built-in metrics. It does not prove the strategy is profitable.

Main weaknesses:
- only `33` trades
- tiny net profit
- no slippage sensitivity
- one market and one date slice
- one open trade at finish
- short side is weaker than long side

Verdict: keep as baseline control, not a paper-trade candidate.
