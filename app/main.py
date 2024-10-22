from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_async_db
from app.models import CurrencyRate

app = FastAPI()


@app.get("/rates")
async def get_rates(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(CurrencyRate))
    rates = result.scalars().all()
    return rates


@app.get("/rates/{symbol}")
async def get_rates_by_symbol(
    symbol: str, db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(CurrencyRate).filter(CurrencyRate.symbol == symbol).first()
    )
    rate = result.scalars().first()
    if rate is None:
        return {"Ошибка: Символ не найден."}
    return rate
