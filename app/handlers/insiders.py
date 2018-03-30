"""
Создать веб-интерфейс, который на /%TICKER%/insider будет отдавать веб-страницу с данными торговли владельцев компании.
На эту страницу попадать по ссыле со страницы /%TICKER%/.
"""
import logging
from aiohttp.web import json_response
from aiohttp_jinja2 import template

from app.models import Ticker, Trade, Insider

log = logging.getLogger(__name__)


async def get_trades(db_manager, ticker):
    ticker_db = await db_manager.get(Ticker, symbol=ticker)
    trades = await db_manager.execute(
        Trade.select(Trade, Insider).join(Insider).where(Trade.ticker == ticker_db).order_by(Trade.last_date.desc()))

    result = []
    for trade in trades:
        new_trade = trade.as_json()
        new_trade['insider'] = trade.insider.name
        result.append(new_trade)

    log.debug(f'Trades for {ticker}: {trades}.')
    return result


@template('insiders.html')
async def insiders_handler(request):
    ticker = request.match_info['ticker'].upper()
    db_manager = request.app['db_manager']

    trades = await get_trades(db_manager, ticker)
    return {
        'trades': trades,
        'ticker': ticker,
    }


async def api_insiders_handler(request):
    ticker = request.match_info['ticker'].upper()
    db_manager = request.app['db_manager']

    trades = await get_trades(db_manager, ticker)
    return json_response(trades)
