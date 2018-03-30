import logging
import urllib.parse
from datetime import date
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import bs4
import requests

from app.models import Ticker, Price, Insider, Trade


log = logging.getLogger(__name__)
PERIOD = '3m'  # 3 months


def to_float(string):
    if string:
        return float(string.replace(',', ''))


def get_last_page(soup):
    last_page_link = soup.find("a", {"id": "quotes_content_left_lb_LastPage"})
    if last_page_link is not None:
        last_page_link = last_page_link["href"]
        query_str = urllib.parse.urlparse(last_page_link).query
        last_page = int(urllib.parse.parse_qs(query_str)["page"][0])
    else:
        last_page = 1

    return min((last_page, 10))


def parse_prices(db_ticker):
    ticker = db_ticker.symbol
    log.info(f'Price parsing for {ticker}')

    data = f'{PERIOD}|false|{ticker}'
    resp = requests.post(
        url=f'https://www.nasdaq.com/symbol/{ticker.lower()}/historical',
        data=data,
        headers={'content-type': 'application/json'},
    )
    soup = bs4.BeautifulSoup(resp.text, 'html.parser')

    trs = soup.find_all('tr')[2:]
    for tr in trs:
        tds = tr.find_all("td")
        price_date = tds[0].text.strip()
        if ':' in price_date:
            log.debug('Specified time. Using the current date.')
            price_date = date.today()
        else:
            price_date = datetime.strptime(price_date, '%m/%d/%Y').date()

        Price.get_or_create(
            date=price_date,
            open=to_float(tds[1].text),
            high=to_float(tds[2].text),
            low=to_float(tds[3].text),
            close=to_float(tds[4].text),
            volume=to_float(tds[5].text),
            ticker=db_ticker,
        )


def parse_trades(db_ticker):
    ticker = db_ticker.symbol
    log.info(f'Trades parsing for {ticker}')

    last_page_detected = False
    last_page = 10
    page_num = 1

    while page_num <= last_page:
        resp = requests.get(f'http://www.nasdaq.com/symbol/{ticker.lower()}/insider-trades?page={page_num}')
        page_num += 1

        soup = bs4.BeautifulSoup(resp.text, 'html.parser')

        if not last_page_detected:
            last_page = get_last_page(soup)
            last_page_detected = True

        div = soup.find("div", {"class": "genTable"})
        trs = div.find_all('tr')[1:]

        for tr in trs:
            tds = tr.find_all("td")

            insider_name = tds[0].find("a").text.upper().strip()
            insider = Insider.get_or_create(name=insider_name)[0]

            last_date = datetime.strptime(tds[2].text.strip(), '%m/%d/%Y').date()
            last_price = to_float(tds[6].text)

            Trade.get_or_create(
                insider=insider,
                last_date=last_date,
                transaction_type=tds[3].text.strip(),
                owner_type=tds[4].text.strip(),
                shares_trades=to_float(tds[5].text),
                last_price=last_price,
                shares_held=to_float(tds[7].text),
                ticker=db_ticker,
            )


def _parse(ticker):
    db_ticker = Ticker.get_or_create(symbol=ticker)[0]

    parse_prices(db_ticker)
    parse_trades(db_ticker)


def parse(filepath, threads_count):
    with open(filepath, 'rt') as fd:
        tickers = fd.read().split()

    pool = ThreadPoolExecutor(threads_count)
    for _ in pool.map(_parse, tickers):
        pass
