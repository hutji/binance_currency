# Binance Currency Rates API
Этот проект представляет собой API для получения и сохранения курсов валют с Binance. API использует FastAPI для обработки запросов и SQLAlchemy для взаимодействия с базой данных.

***- Создаем файл .env в корневой директории с содержанием .env-example:***

## Для локального запуска:
Запуск воркера: 
```
python -m app.worker
```
Запуск приложения: 
```
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

***- Локально документация доступна по адресу:***
```
http://127.0.0.1:8000/docs/
```

### Собираем контейнеры:

Из infra разверните контейнеры при помощи docker-compose:
```
sudo docker-compose up --build
```
## API эндпоинты:
* ```/rates```
``` json
GET
[
    {
        "price": 0.03897,
        "id": 1,
        "symbol": "ETHBTC"
    },
    {
        "price": 0.001035,
        "id": 2,
        "symbol": "LTCBTC"
    },
    {
        "price": 0.008791,
        "id": 3,
        "symbol": "BNBBTC"
    },
]
```
* ```/rates/{symbol}```
``` json
GET
[
    {
        "price": 67442.19,
        "id": 12,
        "symbol": "BTCUSDT"
    }
]
```
