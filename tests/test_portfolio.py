import pytest
from pytrade.assets import FxRate, Stock, Cash, Portfolio


def test_portfolio_init():
    portfolio = Portfolio("AUD")
    assert portfolio.base_currency_code == "AUD"
    assert portfolio.value == 0


def test_base_currency():
    with pytest.raises(TypeError):
        Portfolio(123)
    with pytest.raises(ValueError):
        Portfolio("AUDX")
    portfolio = Portfolio("AUD")
    assert portfolio.base_currency_code == "AUD"
    with pytest.raises(AttributeError):
        # base currency code is read only after init
        portfolio.base_currency_code = "USD"


def test_transfer_basec_currency():
    portfolio = Portfolio("AUD")
    aud = Cash("AUD")
    portfolio.transfer(aud, 1000)
    assert portfolio.value == 1000


def test_transfer_cash_multiple_currencies():
    portfolio = Portfolio("AUD")
    assert portfolio.value == 0

    aud = Cash("AUD")
    usd = Cash("USD")
    audusd = FxRate("AUDUSD", 0.65)

    portfolio.transfer(aud, 1000)
    assert portfolio.value == 1000

    portfolio.transfer(usd, 1000)
    assert portfolio.value == 1000 + 1000 / audusd.rate


def test_transfer_stock():
    portfolio = Portfolio("AUD")
    assert portfolio.value == 0
    zzb = Stock("ZZB AU", 2.50, currency_code="AUD")
    portfolio.transfer(zzb, 1000)
    assert portfolio.value == 1000 * 2.50

    aapl = Stock("AAPL US", 110, currency_code="USD")

    audusd = FxRate("AUDUSD", 0.65)
    portfolio.transfer(aapl, 1000)
    assert portfolio.value == 1000 * 2.50 + 1000 * 110 / audusd.rate

    portfolio.transfer(aapl, -1000)
    assert portfolio.value == 1000 * 2.50  # just zzb left

    portfolio.transfer(zzb, -1000)
    assert portfolio.value == 0


def test_cash_holdings_observed():
    portfolio = Portfolio("AUD")
    assert portfolio.value == 0

    aud = Cash("AUD")
    portfolio.transfer(aud, 1000)
    assert portfolio.value == 1000

    usd = Cash("USD")
    audusd = FxRate("AUDUSD", 0.65)
    portfolio.transfer(usd, 1000)
    assert portfolio.value == 1000 + 1000 / audusd.rate
    audusd.rate == 0.55
    assert portfolio.value == 1000 + 1000 / audusd.rate
    audusd.rate == 0.75
    assert portfolio.value == 1000 + 1000 / audusd.rate


def test_stock_observed():
    portfolio = Portfolio("AUD")
    zzb = Stock("ZZB AU", 2.50, currency_code="AUD")
    portfolio.transfer(zzb, 1000)
    assert portfolio.value == 1000 * 2.50
    zzb.price = 2
    assert portfolio.value == 1000 * 2

    aapl = Stock("AAPL US", 120, currency_code="USD")
    audusd = FxRate("AUDUSD", 0.65)
    portfolio.transfer(aapl, 1000)
    assert round(portfolio.value, 1) == round(
        1000 * 2 + 1000 * 120 / audusd.rate, 1
    )
    aapl.price = 130
    assert round(portfolio.value, 1) == round(
        1000 * 2 + 1000 * 130 / audusd.rate, 1
    )
    audusd.rate = 0.75
    assert round(portfolio.value, 1) == round(
        1000 * 2 + 1000 * 130 / audusd.rate, 1
    )


def test_portfolio_trade():
    portfolio = Portfolio("AUD")
    aud = Cash("AUD")
    portfolio.transfer(aud, 1000)
    assert portfolio.value == 1000

    assert portfolio.get_holding_units("ZZB AU") == 0
    zzb = Stock("ZZB AU", 2.50, currency_code="AUD")
    portfolio.trade(zzb, 100)
    assert portfolio.get_holding_units("ZZB AU") == 100
    assert portfolio.get_holding_units("AUD") == 750
    assert portfolio.value == 1000

    aapl = Stock("AAPL US", 120, currency_code="USD")
    audusd = FxRate("AUDUSD", 0.65)
    portfolio.trade(aapl, 1)
    assert portfolio.get_holding_units("ZZB AU") == 100
    assert portfolio.get_holding_units("AUD") == 750
    assert portfolio.get_holding_units("AAPL US") == 1
    assert portfolio.get_holding_units("USD") == -120

    assert portfolio.value == 1000  # no prices have moved yet
    zzb.price = 2.40
    aapl.price = 130
    audusd.rate = 0.7

    expected_value = (
        +2.40 * 100  # zzb stock
        + 750 * 1  # aud cash
        + 130 * 1 / 0.7  # aapl stock
        - 120 * 1 / 0.7  # usd cash
    )
    assert round(portfolio.value, 1) == round(expected_value, 1)
