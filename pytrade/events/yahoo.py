""" A factory pattern for downloading yahoo data for different objects. """
from abc import ABC, abstractmethod
from datetime import datetime, date
from pytrade.assets import Asset, FxRate
from pytrade.util import clean_column_name, to_datetime
from pytrade.backtest import Backtest
from pytrade.events import (
    AssetPriceEvent,
    FxRateEvent,
    IndicatorEvent,
)
from pandas_datareader import data as web


def fetch_yahoo(ticker, start_date, end_date):
    df = web.DataReader(ticker, "yahoo", start_date, end_date)
    df.columns = [clean_column_name(column) for column in df.columns]
    return df


def load_yahoo_prices(
    instances,
    *args,
    **kwargs,
):
    if isinstance(instances, list):
        for instance in instances:
            _load_one(instance, *args, **kwargs)
    else:
        _load_one(instances, *args, **kwargs)


def _load_one(instance, *args, **kwargs):
    if isinstance(instance, Asset):
        YahooAssetLoader(instance, *args, **kwargs).load()
    elif isinstance(instance, FxRate):
        YahooFxRateLoader(instance, *args, **kwargs).load()
    elif isinstance(instance, str):
        YahooIndicatorLoader(instance, *args, **kwargs).load()
    else:
        raise NotImplementedError("Unsupported instance for yahoo loading.")


class Loader(ABC):
    """ Load data relating to a specific object instance. """
    def __init__(
        self,
        instance,
        backtest,
        *,
        start_date=date(1971, 1, 1),
        end_date=datetime.now().date(),
    ):
        if not isinstance(backtest, Backtest):
            raise TypeError("Expecting Backtest instance.")
        self._instance = instance
        self._backtest = backtest
        self._start_date = to_datetime(start_date)
        self._end_date = to_datetime(end_date)

    @abstractmethod
    def load(self):
        raise NotImplementedError()  # pragma: no cover

    def _create_events(self, ticker):
        events_map = {
            YahooAssetLoader: AssetPriceEvent,
            YahooFxRateLoader: FxRateEvent,
            YahooIndicatorLoader: IndicatorEvent,
        }

        instance = self._instance
        start_date = self._start_date
        end_date = self._end_date
        backtest = self._backtest
        df = fetch_yahoo(ticker, start_date, end_date)
        EventClass = events_map[self.__class__]
        for event_datetime, row in df.iterrows():
            close = float(row["adj_close"])
            event = EventClass(
                instance, event_datetime, close, backtest=backtest
            )
            if event_datetime < start_date or event_datetime > end_date:
                continue  # pragma: no cover just in case yahoo has bad data
            backtest.load_event(event)


class YahooAssetLoader(Loader):
    def load(self):
        asset = self._instance
        ticker = asset.yahoo_ticker
        if ticker is None:
            ticker = asset.code
        if not isinstance(ticker, str):
            raise TypeError("Expecting string.")
        self._create_events(ticker)


class YahooFxRateLoader(Loader):
    def load(self):
        fx_rate = self._instance
        ticker = fx_rate.pair + "=X"
        self._create_events(ticker)


class YahooIndicatorLoader(Loader):
    def load(self):
        self._create_events(self._instance)
