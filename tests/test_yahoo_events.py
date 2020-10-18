import pytest
from pytrading.assets import reset, Stock
from pytrading.strategy import Strategy
from pytrading.backtest import Backtest
from pytrading.events.yahoo import (
    load_yahoo_prices,
    YahooAssetLoader,
)


def test_load_one():
    with pytest.raises(NotImplementedError):
        load_yahoo_prices(None)  # not a supported type


def test_loader():
    reset()
    with pytest.raises(TypeError):
        # requires a backtest object
        YahooAssetLoader(None, None)

    class MyStrategy(Strategy):
        def generate_trades(self):
            return None

    stock = Stock("AAPL")
    stock.yahoo_ticker = 123
    backtest = Backtest(MyStrategy())
    # yahoo_ticker for stock must be None or string
    with pytest.raises(TypeError):
        YahooAssetLoader(stock, backtest).load()
