import pytest
from pytrade.assets import Stock, Currency
from pytrade.observable import Observable


def test_is_observable():
    """ All assets must be observable. """
    usd = Currency("USD")
    stock = Stock("AAPL", quoted_currency=usd)
    assert isinstance(stock, Observable)
    assert isinstance(usd, Observable)


def test_default_ccy_usd():
    """ Check that assets have a default USD currency. """
    stock = Stock("AAPL")
    assert stock.currency.ticker == "USD"


def test_is_unique():
    """ Each asset must have a unique ticker. """
    stock = Stock("AAPL")
    with pytest.raises(ValueError):
        Stock("AAPL")
    assert stock.ticker == "AAPL"


def test_currency_length():
    """ All currency must have ticker of length 3.
        e.g. 'AUD', 'GBP', 'USDHKD'
    """
    audusd = Currency("AUDUSD")
    gbpusd = Currency("GBPUSD")
    assert audusd.ticker == "AUDUSD"
    assert gbpusd.ticker == "GBPUSD"
    with pytest.raises(ValueError):
        Currency("XXXX")
