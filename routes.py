from jesse.enums import exchanges


routes = [
    {
        'exchange': exchanges.SANDBOX,
        'symbol': 'BTC-USDT',
        'timeframe': '1h',
        'strategy': 'BaselineMaTrend',
    },
]

extra_candles = []
