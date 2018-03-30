import logging

from argparse import ArgumentParser

import aiohttp_jinja2
import jinja2
from aiohttp.web import Application, run_app

from app.handlers.analytics import analytics_handler, api_analytics_handler
from app.handlers.delta import delta_handler, api_delta_handler
from app.handlers.insider import insider_handler, api_insider_handler
from app.handlers.insiders import insiders_handler, api_insiders_handler
from app.handlers.ticker import ticker_handler, api_ticker_handler
from app.middleware import error_middleware
from app.models import init_db
from app.handlers.tickers import tickers_handler, api_tickers_handler
from app.parser import parse


log = logging.getLogger('parser')


def parse_args():
    parser = ArgumentParser(prog='tickers')

    parser.add_argument('-d', '--db-name', type=str, required=True, help='Database name')
    parser.add_argument('-u', '--db-user', type=str, required=True, help='Postgres user')
    parser.add_argument('-p', '--db-pass', type=str, required=True, help='Postgres user\' password')

    parser.add_argument('--db-host', type=str, default='127.0.0.1', help='Postgres host')
    parser.add_argument('--db-port', type=int, default=5432, help='Postgres port')

    parser.add_argument('--host', type=str, default='127.0.0.1', help='Listen on this address')
    parser.add_argument('--port', type=int, default=8080, help='Listen on this port')

    parser.add_argument('--tickers-file', type=str, help='Path to the file wih tickers')
    parser.add_argument('--threads-count', type=int, default=1, help='Parsing threads count')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    db_manager = init_db(args.db_name, args.db_user, args.db_pass, args.db_host, args.db_port)

    if args.tickers_file:
        parse(args.tickers_file, args.threads_count)

    handlers = (
        ('GET', '', tickers_handler),
        ('GET', '/api', api_tickers_handler),

        ('GET', '/{ticker:\w+}', ticker_handler),
        ('GET', '/api/{ticker:\w+}', api_ticker_handler),

        ('GET', '/{ticker}/insider', insiders_handler),
        ('GET', '/api/{ticker}/insider', api_insiders_handler),

        ('GET', '/{ticker}/insider/{name}', insider_handler),
        ('GET', '/api/{ticker}/insider/{name}', api_insider_handler),

        ('GET', '/{ticker}/analytics', analytics_handler),
        ('GET', '/api/{ticker}/analytics', api_analytics_handler),

        ('GET', '/{ticker}/delta', delta_handler),
        ('GET', '/api/{ticker}/delta', api_delta_handler),
    )

    app = Application(middlewares=[error_middleware])
    app['db_manager'] = db_manager

    for handler in handlers:
        app.router.add_route(*handler)

    aiohttp_jinja2.setup(app, loader=jinja2.PackageLoader('app', 'templates'))

    run_app(app, host=args.host, port=args.port)


if __name__ == '__main__':
    main()
