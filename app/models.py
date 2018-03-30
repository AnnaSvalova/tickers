from datetime import date

import peewee_async
from peewee import Proxy, Model, CharField, ForeignKeyField, DateField, FloatField


db_proxy = Proxy()


class BaseModel(Model):
    class Meta:
        database = db_proxy


class Ticker(BaseModel):
    """Акции"""
    symbol = CharField(unique=True)

    def as_json(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
        }


class Price(BaseModel):
    """История изменения цен на акции"""
    date = DateField()
    open = FloatField()
    high = FloatField()
    low = FloatField()
    close = FloatField()
    volume = FloatField()

    ticker = ForeignKeyField(Ticker, related_name='prices')

    def as_json(self):
        return {
            'id': self.id,
            'date': date.strftime(self.date, '%d-%m-%Y'),
            'open': round(self.open, 3),
            'high': round(self.high, 3),
            'low': round(self.low, 3),
            'close': round(self.close, 3),
            'volume': round(self.volume, 3),
            'ticker_id': self.ticker_id,
        }


class Insider(BaseModel):
    name = CharField(unique=True)

    def as_json(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class Trade(BaseModel):
    last_date = DateField()
    transaction_type = CharField()
    owner_type = CharField()
    shares_trades = FloatField()
    last_price = FloatField(null=True)
    shares_held = FloatField()

    ticker = ForeignKeyField(Ticker, related_name='trades')
    insider = ForeignKeyField(Insider, related_name='trades')

    def as_json(self):
        return {
            'id': self.id,
            'last_date': date.strftime(self.last_date, '%d-%m-%Y'),
            'transaction_type': self.transaction_type,
            'owner_type': self.owner_type,
            'shares_trades': round(self.shares_trades, 3),
            'last_price': round(self.last_price, 3) if self.last_price else '',
            'shares_held': round(self.shares_held, 3),
            'insider_id': self.insider_id,
            'ticker_id': self.ticker_id,
        }


def init_db(db_name: str, db_user: str, db_pass: str, host: str, port: int):
    db = peewee_async.PostgresqlDatabase(db_name, user=db_user, password=db_pass, host=host, port=port)
    db_proxy.initialize(db)

    Ticker.create_table(True)
    Price.create_table(True)
    Insider.create_table(True)
    Trade.create_table(True)

    objects = peewee_async.Manager(db_proxy)

    return objects
