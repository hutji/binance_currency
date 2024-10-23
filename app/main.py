import json

import redis.asyncio as redis
from fastapi import Depends, FastAPI, HTTPException
from fastapi.websockets import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_async_db
from app.logger import setup_logger
from app.models import CurrencyRate

app = FastAPI()
logger = setup_logger()

redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)


@app.get("/rates")
async def get_rates(db: AsyncSession = Depends(get_async_db)):
    logger.info("Достаем стоимость из БД")
    cached_rates = await redis_client.get("all_rates")
    if cached_rates:
        logger.info("Возвращаем кешированные данные")
        return json.loads(cached_rates)

    result = await db.execute(select(CurrencyRate))
    rates = result.scalars().all()
    await redis_client.set(
        "all_rates", json.dumps([rate.to_dict() for rate in rates])
    )
    logger.info("Возвращаем последние данные")
    return rates


@app.get("/rates/{symbol}")
async def get_rates_by_symbol(
    symbol: str, db: AsyncSession = Depends(get_async_db)
):
    logger.info(f"Получаем стоимость по символу {symbol}")
    cached_rate = await redis_client.get(f"rate_{symbol}")
    if cached_rate:
        logger.info(f"Возвращем кешированную стоимость по символу {symbol}")
        return json.loads(cached_rate)

    result = await db.execute(
        select(CurrencyRate).filter(CurrencyRate.symbol == symbol)
    )
    rate = result.scalars().first()
    if rate is None:
        logger.warning(f"Символ не найден: {symbol}")
        raise HTTPException(status_code=404, detail="Ошибка: Символ не найден")
    await redis_client.set(f"rate_{symbol}", json.dumps(rate.to_dict()))
    return rate


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Установлено соединение с вебсокетом")
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Получено сообщение: {data}")
            await websocket.send_text(f"Сообщение: {data}")
    except Exception as err:
        print(err)
    finally:
        await websocket.close()
