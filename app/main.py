import json

import redis.asyncio as redis
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_async_db
from app.models import CurrencyRate

app = FastAPI()

redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)


@app.get("/rates")
async def get_rates(db: AsyncSession = Depends(get_async_db)):
    cached_rates = await redis_client.get("all_rates")
    if cached_rates:
        return json.loads(cached_rates)

    result = await db.execute(select(CurrencyRate))
    rates = result.scalars().all()
    await redis_client.set(
        "all_rates", json.dumps([rate.to_dict() for rate in rates])
    )
    return rates


@app.get("/rates/{symbol}")
async def get_rates_by_symbol(
    symbol: str, db: AsyncSession = Depends(get_async_db)
):
    cached_rate = await redis_client.get(f"rate_{symbol}")
    if cached_rate:
        return json.loads(cached_rate)

    result = await db.execute(
        select(CurrencyRate).filter(CurrencyRate.symbol == symbol)
    )
    rate = result.scalars().first()
    if rate is None:
        raise HTTPException(
            status_code=404, detail="Ошибка: Символ не найден."
        )
    await redis_client.set(f"rate_{symbol}", json.dumps(rate.to_dict()))
    return rate
