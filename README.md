# binance_currency

Для локального запуска:
Запуск воркера: python -m app.worker
Запуск фастапи: uvicorn app.main:app --host 0.0.0.0 --port 8000

/rates
    {
        "price": 0.03904,
        "id": 1,
        "symbol": "ETHBTC"
    },

/rates/BTCUSDT
    {
        "price": 67442.19,
        "id": 12,
        "symbol": "BTCUSDT"
    }
