# Jesse.Trade Example Strategy References

This is the strategy-reference intake layer for the Gas Town Backtesting Desk.

The public Jesse.Trade strategy pages expose names, routes, date ranges, and reported metrics. The strategy source code is behind the account-only `Get Strategy` action, so this repo stores a public metadata catalog and a safe local import path for code you download from your account.

## Public Reference Catalog

The machine-readable catalog lives at:

```text
references/jesse-trade-strategies/catalog.json
```

Use it for:

- strategy idea generation
- archetype selection
- benchmark selection
- deciding which account-downloaded source files are worth importing first
- Backtesting Desk tournaments

## Discovered Public Strategies

| Strategy | Tier | Route | Period | Reported PNL | Sharpe | Max DD | Trades | Source |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| TemaTrendFollowing | free | BTC-USDT 30m | 2024-01-01 to 2024-12-31 | 309.26% | 2.97 | -25.99% | 67 | https://jesse.trade/strategies/tematrendfollowing |
| ADXWilliamsStrategy | free | BTC-USDT 15m | 2022-01-01 to 2022-12-31 | 210.62% | 1.98 | -25.20% | 56 | https://jesse.trade/strategies/adxwilliamsstrategy |
| KAMA_TrendFollowing | free | BTC-USDT 15m | 2022-01-01 to 2022-12-31 | 147.28% | 2.08 | -23.55% | 128 | https://jesse.trade/strategies/kama-trendfollowing |
| Turtle V2 | premium | BTC-USDT 1h | 2022-01-01 to 2022-12-31 | 118.23% | 1.79 | -16.61% | 68 | https://jesse.trade/strategies/turtle-v2 |
| TrendWaveRiderV2 | premium | BTC-USDT 15m | 2024-01-01 to 2024-12-31 | 108.27% | 2.18 | -19.59% | 67 | https://jesse.trade/strategies/trendwaveriderv2 |
| Turtle V3 | premium | BTC-USDT 1h | 2022-01-01 to 2022-12-31 | 96.48% | 1.69 | -19.05% | 72 | https://jesse.trade/strategies/turtle-v3 |
| AlligatorV2 | premium | BTC-USDT 30m | 2022-01-01 to 2022-12-31 | 90.14% | 1.77 | -13.89% | 37 | https://jesse.trade/strategies/alligatorv2 |
| TurtleAI | free | BTC-USDT 1h | 2023-01-01 to 2023-12-31 | 73.65% | 1.65 | -11.86% | 35 | https://jesse.trade/strategies/turtleai-by-o1-preview-model |
| CloudScalper | free | BTC-USDT 15m | 2022-01-01 to 2022-12-31 | 73.25% | 1.29 | -30.81% | 95 | https://jesse.trade/strategies/cloudscalper |
| TrendSwingTrader V2 | premium | BTC-USDT 4h | 2022-01-01 to 2022-12-31 | 70.80% | 1.95 | -10.73% | 30 | https://jesse.trade/strategies/trendswingtrader-v2 |
| TrendSwingTrader V1 | free | BTC-USDT 4h | 2022-01-01 to 2022-12-31 | 68.00% | 1.11 | -41.40% | 30 | https://jesse.trade/strategies/trendswingtrader-v1 |
| AlligatorAI | free | BTC-USDT 30m | 2022-01-01 to 2022-12-31 | 67.70% | 1.61 | -14.00% | 41 | https://jesse.trade/strategies/alligatorai-by-o1-preview-model |
| IchimokuCloud | free | BTC-USDT 1h | 2023-01-01 to 2023-12-31 | 62.13% | 1.03 | -28.43% | 19 | https://jesse.trade/strategies/ichimokucloud |
| SuperScalper | premium | BTC-USDT 15m | 2022-01-01 to 2022-12-31 | 59.41% | 1.93 | -12.47% | 132 | https://jesse.trade/strategies/superscalper |
| MeanReversionRSI | free | BTC-USDT 1h | 2024-01-01 to 2024-12-31 | 45.36% | 2.63 | -1.63% | 7 | https://jesse.trade/strategies/meanreversionrsi |
| Slow Trend Following | premium | BTC-USDT 6h | 2024-02-01 to 2024-02-29 | 37.69% | 9.43 | -1.49% | 5 | https://jesse.trade/strategies/slow-trend-following |
| Trend Following | free | BTC-USDT 4h | 2022-01-01 to 2022-12-31 | 24.44% | 1.02 | -14.73% | 87 | https://jesse.trade/strategies/trend-following-by-o1-preview-model |
| DonchianATRTrend | unknown | ETH-USDT 1h | 2024-01-01 to 2024-12-31 | 12.20% | 0.74 | -11.03% | 100 | https://jesse.trade/strategies/donchianatrtrend |
| EMBIA | unknown | BTC-USDT 5m | 2025-10-01 to 2025-10-31 | 11.26% | 3.51 | -6.35% | 9 | https://jesse.trade/strategies/embia |
| RSI Trend | free | BTC-USDT 1h | 2023-09-01 to 2023-09-30 | 1.27% | 1.03 | -2.80% | 16 | https://jesse.trade/strategies/rsi-trend |
| MACD + EMA | unknown | BTC-USDT 1h | 2022-05-01 to 2022-05-31 | -8.53% | -2.21 | -17.11% | 14 | https://jesse.trade/strategies/macd-ema |
| Golden Cross Strategy | unknown | BTC-USDT 4h | 2023-02-01 to 2023-02-28 | -18.86% | -4.84 | -22.63% | 4 | https://jesse.trade/strategies/golden-cross-strategy |
| IFR2 | unknown | BTC-USDT 1h | 2022-08-01 to 2022-08-31 | no trades | n/a | n/a | 0 | https://jesse.trade/strategies/ifr2 |
| TrendWaveRider | free | BTC-USDT 15m | March 2026 filter | generating metrics | n/a | n/a | n/a | https://jesse.trade/strategies/trendwaverider |

## Safe Source Import

Automated account download:

```bash
cd /Users/lg/gt/jesse_gas_town/crew/lg
./scripts/download-jesse-trade-strategies.py --account "your-account-or-email" --tiers premium,free,unknown
```

The script opens Chrome with a local DevTools session, prompts for the password without echoing it, clicks each `Get Strategy` action, and writes any downloaded or captured code to the gitignored source directory.

Download strategy source files from your Jesse.Trade account and import them locally:

```bash
cd /Users/lg/gt/jesse_gas_town/crew/lg
./scripts/import-jesse-trade-strategy-export.sh /path/to/downloaded/strategies
```

Imported code is written to:

```text
references/jesse-trade-strategies/source/
```

That folder is gitignored by default so account-only strategy source is not pushed accidentally. If you explicitly want those sources committed to your private repo, remove the ignore rule after checking the Jesse.Trade terms for your account.

## Backtesting Desk Use

After importing account source, create a desk tournament:

```bash
bd mol pour jt-strategy-reference-intake \
  --var source_dir="references/jesse-trade-strategies/source" \
  --var objective="Classify and rank downloaded Jesse.Trade example strategies for HPO candidates"
```

Then sling the molecule:

```bash
gt sling <molecule-id> jesse_gas_town --crew lg --agent codex-jesse --merge=local \
  --args "Use $jesse-gas-town-strategy-lab. Treat imported Jesse.Trade examples as reference inputs, not live candidates."
```
