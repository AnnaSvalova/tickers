"""
Создать веб-интерфейс, который на /%TICKER%/analytics?date_from=..&date_to=... будет отдавать веб-страницу с данными о
разнице цен в текущих датах(нужна разница всех цен - открытия, закрытия, максимума, минимума)
"""
import logging
from aiohttp.web import json_response
from aiohttp_jinja2 import template

from app.models import Price, Ticker

log = logging.getLogger(__name__)


async def get_analytics(db_manager, ticker, date_from, date_to):
    """Получить разницу цен по заданной акции в текущих датах"""
    ticker = await db_manager.get(Ticker, symbol=ticker)

    prices_from = await db_manager.get(Price, ticker=ticker, date=date_from)
    prices_from = prices_from.as_json()
    prices_to = await db_manager.get(Price, ticker=ticker, date=date_to)
    prices_to = prices_to.as_json()

    return {
        'open': prices_to['open'] - prices_from['open'],
        'high': prices_to['high'] - prices_from['high'],
        'low': prices_to['low'] - prices_from['low'],
        'close': prices_to['close'] - prices_from['close'],
    }


async def get_available_dates(db_manager, ticker):
    ticker = await db_manager.get(Ticker, symbol=ticker)
    dates = await db_manager.execute(
        Price.select(Price.date).where(Price.ticker_id == ticker).order_by(Price.date.desc()))
    dates = [date.date for date in dates]

    return dates


@template('analytics.html')
async def analytics_handler(request):
    ticker = request.match_info['ticker'].upper()
    date_from = request.query.get('date_from', None)
    date_to = request.query.get('date_to', None)

    db_manager = request.app['db_manager']

    if date_from is None or date_to is None:
        result = None
        dates = await get_available_dates(db_manager, ticker)
    else:
        result = await get_analytics(db_manager, ticker, date_from, date_to)
        dates = None

    log.debug(f'Result: {result}, dates: {dates}.')
    return {
        'result': result,
        'dates': dates,
        'date_from': date_from,
        'date_to': date_to,
    }


async def api_analytics_handler(request):
    ticker = request.match_info['ticker'].upper()
    date_from = request.query.get('date_from', None)
    date_to = request.query.get('date_to', None)

    db_manager = request.app['db_manager']

    if date_from is None or date_to is None:
        raise ValueError('Dates must be filled.')

    result = await get_analytics(db_manager, ticker, date_from, date_to)

    return json_response(result)
