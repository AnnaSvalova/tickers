"""
Создать веб-интерфейс, который на /%TICKER/delta?value=N&type=(open/high/low/close) будет отдавать веб-страницу с
данными о минимальных периодах (дата начала-дата конца), когда указанная цена изменилась более чем на N
Например, с первого по пятое число месяца цена акции прирастала на 2 доллара в день, затем два дня падала на 1
доллар(до 7 числа), и затем выросла на 3 доллара(к 8 числу). 9 числа цена упала на 5 долларов.
Задана разница - 11 долларов. Необходимо показать интервал 1 - 8 число.
Если бы 9 числа цена не упала, а приросла на 5 долларов - минимальный интервал все равно останется с 1 по 8 число.
"""
import logging

from aiohttp.web import json_response
from aiohttp_jinja2 import template
from peewee import RawQuery
from peewee_async import raw_query

from app.models import Price

log = logging.getLogger(__name__)


TYPE_VALUES = ['open', 'close', 'high', 'low']


async def get_delta(ticker, value, column_type):
    sql_query = f'''
        with id as (select id from Ticker where symbol = '{ticker}'),
            prices as (select * from Price join id on id.id = Price.ticker_id)
        select * from Price,
        (select a.date as date_from, b.date as date_to, a.ticker_id as t_id
        from prices as a, prices as b
        where 
              b.{column_type} - a.{column_type} > {value} and 
              b.date > a.date
        order by b.date - a.date
        limit 1) as c
        where Price.ticker_id=c.t_id and Price.date >= c.date_from and Price.date <= c.date_to
        order by Price.date desc
    '''
    return [r.as_json() for r in await raw_query(RawQuery(Price, sql_query))]


async def api_delta_handler(request):
    ticker = request.match_info['ticker'].upper()

    value = float(request.query.get('value'))
    if value <= 0:
        raise ValueError('Value must be greater than 0.')

    column = request.query.get('type', None).lower()
    if column not in TYPE_VALUES:
        raise ValueError('Wrong value of "type" field.')

    delta = await get_delta(ticker, value, column)
    return json_response(delta)


@template('delta.html')
async def delta_handler(request):
    ticker = request.match_info['ticker'].upper()

    value = request.query.get('value', None)
    column = request.query.get('type', None)

    if value is None or column is None:
        return {
            'ticker': ticker,
            'prices': None,
            'types': TYPE_VALUES,
        }

    value = float(value)
    if value <= 0:
        raise ValueError('Value must be greater than 0.')

    column = column.lower()
    if column not in TYPE_VALUES:
        raise ValueError('Wrong value of "type" field.')

    delta = await get_delta(ticker, value, column)

    return {
        'ticker': ticker,
        'prices': delta,
        'types': TYPE_VALUES,
    }
