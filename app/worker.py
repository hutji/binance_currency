import asyncio
import json
import os

import aiohttp
import redis.asyncio as redis
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.logger import setup_logger
from app.models import CurrencyRate

load_dotenv()

redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)
logger = setup_logger()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def get_binance_rates():
    url = "https://api.binance.com/api/v3/ticker/price"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            logger.info("Получение курса валют по api")
            return await response.json()


async def save_rates_to_db(rates):
    async with async_session() as db:
        for rate in rates:
            db_rate = CurrencyRate(
                symbol=rate["symbol"], price=float(rate["price"])
            )
            db.add(db_rate)
        await db.commit()
        logger.info("Курсы сохранены в БД")


async def update_redis_cache(rates):
    try:
        for rate in rates:
            symbol = rate["symbol"]
            await redis_client.set(f"rate_{symbol}", json.dumps(rate))
            logger.info(f"Курс для {symbol} обновлен в редисе")

        await redis_client.set("all_rates", json.dumps(rates))
        logger.info("Общий список курсов обновлен в редисе")
    except Exception as err:
        print(f"Ошибка при обновлении кэша: {err}")


async def worker():
    while True:
        rates = await get_binance_rates()
        await save_rates_to_db(rates)
        await update_redis_cache(rates)
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(worker())
