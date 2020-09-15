import pytest
from pytrade.assets import FxRate, Stock, Cash, Portfolio
from pytrade.settings import get_default_currency_code


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


def test_default_currency_code():
    portfolio = Portfolio()
    default_code = get_default_currency_code()
    assert portfolio.base_currency_code == default_code


def test_trade_types():
    portfolio = Portfolio("AUD")
    stock = Stock("ZZX AU", 2.50, currency_code="AUD")
    with pytest.raises(TypeError):
        portfolio.trade(None, units=1)
    with pytest.raises(TypeError):
        portfolio.trade(stock, units="1")

    stock.price = None
    with pytest.raises(ValueError):
        # cannot calculate consideration with a None value
        portfolio.trade(stock, units=1)

    # consideration must be numeric
    with pytest.raises(TypeError):
        portfolio.trade(stock, units=1, consideration="123")

    # codes such as 'AUD', 'USD', 'GBP'
    # are reserved for cash and shouldn't be used for other assets.
    stock = Stock("AUD", 2.50, currency_code="AUD")
    with pytest.raises(TypeError):
        portfolio.trade(stock, units=1)


def test_portfolio_str():
    portfolio = Portfolio("AUD")
    assert str(portfolio) == "Portfolio('AUD')"

    audusd = FxRate("AUDUSD", 0.7)  # noqa: F841
    assert audusd.rate == 0.7
    stock1 = Stock("CCC US", 1530, currency_code="USD")
    stock2 = Stock("DDD US", 1520, currency_code="USD")
    portfolio.transfer(stock1, 100)
    portfolio.transfer(stock2, 200)
    portfolio_str = str(portfolio)
    part0 = "Portfolio('AUD'):"
    part1 = "Stock('CCC US', 1530, currency_code='USD'): 100"
    part2 = "Stock('DDD US', 1520, currency_code='USD'): 200"

    parts = portfolio_str.split("\n")
    assert parts[0].strip() == part0
    assert parts[1].strip() == part1
    assert parts[2].strip() == part2


def test_portfolio_weight():
    portfolio = Portfolio("USD")
    stock1 = Stock("ABC US", 2.00, currency_code="USD")
    stock2 = Stock("DEF US", 2.00, currency_code="USD")
    cash = Cash("USD")
    portfolio.transfer(stock1, 100)
    portfolio.transfer(stock2, 100)
    assert portfolio.get_holding_weight("ABC US") == 0.5
    assert portfolio.get_holding_weight("DEF US") == 0.5

    portfolio.transfer(cash, 400)
    assert portfolio.get_holding_weight("USD") == 0.5
    assert portfolio.get_holding_weight("ABC US") == 0.25
    assert portfolio.get_holding_weight("DEF US") == 0.25
