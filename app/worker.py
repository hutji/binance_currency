import asyncio
import os

import aiohttp
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models import CurrencyRate

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def get_binance_rates():
    url = "https://api.binance.com/api/v3/ticker/price"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


async def save_rates_to_db(rates):
    async with async_session() as db:
        for rate in rates:
            db_rate = CurrencyRate(
                symbol=rate["symbol"], price=float(rate["price"])
            )
            db.add(db_rate)
        await db.commit()


async def worker():
    while True:
        rates = await get_binance_rates()
        await save_rates_to_db(rates)
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(worker())
