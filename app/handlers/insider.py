"""
Создать веб-интерфейс, который на /%TICKER%/insider/%NAME% будет отдавать веб-страницу с данными о торговле данного
владельца компании. На эту страницу попадать по ссылке со страницы /%TICKER%/insider
"""
import logging

from aiohttp.web import json_response
from aiohttp_jinja2 import template

from app.models import Ticker, Insider, Trade


log = logging.getLogger(__name__)


async def get_insider(db_manager, ticker, insider_name):
    db_ticker = await db_manager.get(Ticker, symbol=ticker)
    insider = await db_manager.get(Insider, name=insider_name)

    trades = await db_manager.execute(
        Trade.select().where(Trade.ticker == db_ticker, Trade.insider == insider).order_by(Trade.last_date.desc()))
    trades = [t.as_json() for t in trades]

    log.debug(f'Result for ticker {ticker}, insider {insider_name}.')
    return trades


@template('insider.html')
async def insider_handler(request):
    ticker = request.match_info['ticker'].upper()
    insider_name = request.match_info['name'].upper()
    db_manager = request.app['db_manager']

    trades = await get_insider(db_manager, ticker, insider_name)
    return {
        'trades': trades,
        'ticker': ticker,
        'insider': insider_name,
    }


async def api_insider_handler(request):
    ticker = request.match_info['ticker'].upper()
    insider_name = request.match_info['name'].upper()
    db_manager = request.app['db_manager']

    trades = await get_insider(db_manager, ticker, insider_name)
    return json_response(trades)
