import pytest
from pytrade.settings import get_default_currency_code
from pytrade.assets import Asset, Stock
from pytrade.observable import Observable


def test_is_observable():
    """ All assets must be observable. """
    stock = Stock("AAPL", currency_code="USD")
    assert isinstance(stock, Observable)


def test_default_ccy_usd():
    """ Check that assets have a default currency. """
    stock = Stock("AAPL")
    default_code = get_default_currency_code()
    assert stock.currency_code == default_code


def test_is_unique():
    """ Each asset must have a unique ticker. """
    stock = Stock("AAPL")
    with pytest.raises(ValueError):
        Stock("AAPL")
    assert stock.code == "AAPL"


def test_get_asset_for_code():
    Asset.reset()
    stock1 = Stock("GOOG")
    stock2 = Asset.get_asset_for_code("GOOG")
    assert stock1 is stock2


def test_get_instances():
    stock1 = Stock("AAA")
    stock2 = Stock("BBB")
    assets = Asset.get_instances()
    assert len(assets) == 2
    assert stock1 in assets
    assert stock2 in assets


def test_local_value():
    stock = Stock("AAPL")
    assert stock.local_value is None
    stock.price = 300
    assert stock.price == 300
    assert stock.local_value == 300


def test_price_setter():
    stock = Stock(
        code="AAPL",
        currency_code="USD",
        price=121,
    )
    assert stock.code == "AAPL"
    assert stock.currency_code == "USD"
    assert stock.price == 121
    assert stock.local_value == 121

    stock.price = None  # so we cannot value
    assert stock.local_value is None

    stock.price = 120
    assert stock.price == 120
    assert stock.local_value == 120

    with pytest.raises(TypeError):
        stock.price = "123"
