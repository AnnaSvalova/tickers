"""
Создать веб-интерфейс, который на / будет отдавать веб-страницу со ссылками на акции, доступные в базе данных.
"""
import logging

from aiohttp.web import json_response
from aiohttp_jinja2 import template

from app.models import Ticker

log = logging.getLogger(__name__)


async def get_tickers(db_manager):
    result = await db_manager.execute(Ticker.select().order_by(Ticker.symbol))
    result = [r.as_json() for r in result]

    log.debug(f'Received tickers: {result}.')
    return result


@template('tickers.html')
async def tickers_handler(request):
    result = await get_tickers(request.app['db_manager'])
    return {'tickers': [r['symbol'] for r in result]}


async def api_tickers_handler(request):
    result = await get_tickers(request.app['db_manager'])
    return json_response(result)
