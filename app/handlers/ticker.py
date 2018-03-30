"""
создать веб-интерфейс, который на /%TICKER% будет отдавать веб-страницу с таблицей цен на акцию за 3 месяца
"""
import logging
from datetime import timedelta, datetime

from aiohttp.web import json_response
from aiohttp_jinja2 import template

from app.models import Ticker, Price


log = logging.getLogger(__name__)


async def get_prices(db_manager, ticker):
    three_month_ago = datetime.today() - timedelta(days=90)

    ticker_db = await db_manager.get(Ticker, symbol=ticker)

    result = await db_manager.execute(
        Price.select().where(Price.ticker == ticker_db, Price.date >= three_month_ago).order_by(Price.date.desc()))
    result = [price.as_json() for price in result]

    log.debug(f'Prices for {ticker}: {result}.')
    return result


@template('ticker.html')
async def ticker_handler(request):
    ticker = request.match_info['ticker'].upper()
    db_manager = request.app['db_manager']

    prices = await get_prices(db_manager, ticker)
    return {
        'prices': prices,
        'ticker': ticker,
    }


async def api_ticker_handler(request):
    ticker = request.match_info['ticker'].upper()
    db_manager = request.app['db_manager']

    prices = await get_prices(db_manager, ticker)
    return json_response(prices)
