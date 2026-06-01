# Backtest Matrix: BaselineMaTrend BTC/ETH 1h

Date: 2026-06-02
Strategy: `BaselineMaTrend`
Exchange: `Binance Perpetual Futures`
Timeframe: `1h`
Leverage: `1x cross`
Starting balance: `10000`
Data source: imported local Jesse DB `1m` candles resampled by Jesse to `1h`

Raw CSV: `docs/backtests/2026-06-02-baseline-ma-trend-matrix.csv`

## Command

```bash
/Users/lg/src/jesse/.venv/bin/python scripts/run-baseline-ma-trend-matrix.py
```

The matrix ran:

- symbols: `BTC-USDT`, `ETH-USDT`
- regimes: `uptrend` from `2023-10-01` to `2024-03-15`, `choppy` from `2024-03-15` to `2024-06-15`, `downtrend` from `2024-06-15` to `2024-09-15`
- base fees: `0.0004`, `0.0008`
- slippage settings: `0`, `2` bps
- effective fee model: `effective_fee = base_fee + slippage_bps / 10000`

Jesse `research.backtest` has no native slippage setting in this checkout, so
slippage is modeled as extra per-side notional cost through `fee`. This is a
cost-sensitivity proxy, not a fill-price or stop-trigger simulation.

## Baseline Rows

Baseline rows use `base_fee=0.0004` and `slippage_bps=0`.

| Symbol | Regime | Range | Net % | Annual | Max DD | Sharpe | Sortino | Calmar | Win | Trades | Exp. | L/S | Decision |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| BTC-USDT | uptrend | 2023-10-01 to 2024-03-15 | 0.0305 | 0.0670 | -0.0181 | 1.4812 | 3.1487 | 3.6908 | 0.4000 | 30 | 0.1015 | 22/8 | keep baseline control |
| BTC-USDT | choppy | 2024-03-15 to 2024-06-15 | -0.0007 | -0.0026 | -0.0191 | -0.0639 | -0.1102 | -0.1385 | 0.2778 | 18 | -0.0037 | 5/13 | reject |
| BTC-USDT | downtrend | 2024-06-15 to 2024-09-15 | -0.0079 | -0.0315 | -0.0188 | -0.8852 | -1.4884 | -1.6783 | 0.2941 | 17 | -0.0467 | 9/8 | reject |
| ETH-USDT | uptrend | 2023-10-01 to 2024-03-15 | -0.0198 | -0.0436 | -0.0330 | -1.3686 | -1.9373 | -1.3209 | 0.3448 | 29 | -0.0684 | 19/10 | reject |
| ETH-USDT | choppy | 2024-03-15 to 2024-06-15 | -0.0110 | -0.0435 | -0.0119 | -1.5891 | -2.3804 | -3.6706 | 0.3077 | 13 | -0.0844 | 6/7 | reject |
| ETH-USDT | downtrend | 2024-06-15 to 2024-09-15 | 0.0150 | 0.0596 | -0.0190 | 1.3805 | 2.9910 | 3.1425 | 0.3158 | 19 | 0.0790 | 9/10 | keep baseline control |

## Cost Sensitivity

The two viable slices deteriorated as costs increased:

- `BTC-USDT uptrend`: Sharpe fell from `1.4812` at `0.0004` effective fee to `0.7140` at `0.0010`; max drawdown widened from `-0.0181` to `-0.0220`.
- `ETH-USDT downtrend`: Sharpe fell from `1.3805` at `0.0004` effective fee to `0.7196` at `0.0010`; max drawdown widened from `-0.0190` to `-0.0220`.

Rejected slices stayed rejected under every fee/slippage setting.

## Review

This matrix confirms `BaselineMaTrend` is a useful workflow control, not a
paper-trade candidate. It finds isolated positive slices, but performance is
regime-specific, trade counts are modest, and the strategy fails four of six
baseline route/regime cases before optimization.

Verdict: keep as baseline control; reject as alpha candidate. Next useful work is
to test candidate archetypes with a stronger thesis rather than optimize this
baseline.
