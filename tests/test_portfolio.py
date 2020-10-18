import pytest
from pytrading.assets import reset, FxRate, Stock, Cash, Portfolio
from pytrading.compliance import Compliance
from pytrading.broker import Broker
from pytrading.settings import get_default_currency_code


class TestPortfolio(object):

    def setup_method(self, *args):
        reset()
        self.portfolio = Portfolio("AUD")
        self.aud = Cash("AUD")
        self.usd = Cash("USD")
        self.audusd = FxRate("AUDUSD", 0.70)
        self.stock_aud = Stock("ZZB AU", 2.50, currency_code="AUD")
        self.stock_usd = Stock("ZZB US", 110, currency_code="USD")

    def teardown_method(self, *args):
        del self.portfolio
        del self.aud
        del self.usd
        del self.stock_aud
        del self.stock_usd

    def test_portfolio_init(self):
        portfolio = self.portfolio
        assert portfolio.base_currency_code == "AUD"
        assert portfolio.value == 0

    def test_base_currency(self):
        portfolio = self.portfolio
        with pytest.raises(TypeError):
            Portfolio(123, code="ASD")
        with pytest.raises(ValueError):
            Portfolio("AUDX", code="IOP")
        assert portfolio.base_currency_code == "AUD"
        with pytest.raises(AttributeError):
            # base currency code is read only after init
            portfolio.base_currency_code = "USD"

    def test_transfer_base_currency(self):
        self.portfolio.transfer(self.aud, 1000)
        assert self.portfolio.value == 1000

    def test_transfer_cash_multiple_currencies(self):
        portfolio = self.portfolio
        assert portfolio.value == 0
        self.audusd.rate = 0.65

        portfolio.transfer(self.aud, 1000)
        assert portfolio.value == 1000

        portfolio.transfer(self.usd, 1000)
        assert portfolio.value == 1000 + 1000 / self.audusd.rate

    def test_transfer_stock(self):
        portfolio = self.portfolio
        assert portfolio.value == 0
        self.stock_aud.price = 2.50
        self.stock_usd.price = 110
        portfolio.transfer(self.stock_aud, 1000)
        assert portfolio.value == 1000 * 2.50

        self.audusd.rate = 0.65
        portfolio.transfer(self.stock_usd, 1000)
        assert portfolio.value == 1000 * 2.50 + 1000 * 110 / self.audusd.rate

        portfolio.transfer(self.stock_usd, -1000)
        assert portfolio.value == 1000 * 2.50  # just 'ZZB AU' left

        portfolio.transfer(self.stock_aud, -1000)
        assert portfolio.value == 0

    def test_cash_holdings_observed(self):
        portfolio = self.portfolio
        assert portfolio.value == 0

        portfolio.transfer(self.aud, 1000)
        assert portfolio.value == 1000
        audusd = self.audusd
        audusd.rate = 0.65
        portfolio.transfer(self.usd, 1000)
        assert portfolio.value == 1000 + 1000 / audusd.rate
        audusd.rate == 0.55
        assert portfolio.value == 1000 + 1000 / audusd.rate
        audusd.rate == 0.75
        assert portfolio.value == 1000 + 1000 / audusd.rate

    def test_stock_observed(self):
        portfolio = self.portfolio
        portfolio.transfer(self.stock_aud, 1000)
        self.stock_aud.price = 2.50
        assert portfolio.value == 1000 * 2.50
        self.stock_aud.price = 2
        assert portfolio.value == 1000 * 2

        audusd = self.audusd
        audusd.rate = 0.65
        portfolio.transfer(self.stock_usd, 1000)
        self.stock_usd.price = 120
        assert round(portfolio.value, 1) == round(
            1000 * 2 + 1000 * 120 / audusd.rate, 1
        )
        self.stock_usd.price = 130
        assert round(portfolio.value, 1) == round(
            1000 * 2 + 1000 * 130 / audusd.rate, 1
        )
        audusd.rate = 0.75
        assert round(portfolio.value, 1) == round(
            1000 * 2 + 1000 * 130 / audusd.rate, 1
        )

    def test_portfolio_trade(self):
        portfolio = self.portfolio
        portfolio.transfer(self.aud, 1000)
        assert portfolio.get_holding_units("ZZB AU") == 0
        self.stock_aud.price = 2.50
        portfolio.trade(self.stock_aud, 100)
        assert portfolio.get_holding_units("ZZB AU") == 100
        assert portfolio.get_holding_units("AUD") == 750
        assert portfolio.value == 1000

        self.audusd.rate = 0.65
        self.stock_usd.price = 120
        portfolio.trade(self.stock_usd, 1)
        assert portfolio.get_holding_units("ZZB AU") == 100
        assert portfolio.get_holding_units("AUD") == 750
        assert portfolio.get_holding_units("ZZB US") == 1
        assert portfolio.get_holding_units("USD") == -120

        assert portfolio.value == 1000  # no prices have moved yet
        self.stock_aud.price = 2.40
        self.stock_usd.price = 130
        self.audusd.rate = 0.7

        expected_value = (
            + 2.40 * 100  # zzb au stock
            + 750 * 1  # aud cash
            + 130 * 1 / 0.7  # zzb us stock
            - 120 * 1 / 0.7  # usd cash
        )
        assert round(portfolio.value, 1) == round(expected_value, 1)

    def test_portfolio_trade_cash(self):
        portfolio = self.portfolio
        portfolio.transfer(self.aud, 1000)
        assert portfolio.get_holding_units("USD") == 0
        portfolio.trade(self.usd, 100)
        # print(portfolio)
        assert portfolio.get_holding_units("USD") == 100
        assert int(portfolio.get_holding_units("AUD")) == int(1000 - 100 / 0.7)

    def test_default_currency_code(self):
        reset()
        portfolio = Portfolio()
        default_code = get_default_currency_code()
        assert portfolio.base_currency_code == default_code

    def test_trade_types(self):
        portfolio = self.portfolio
        stock = Stock("ZZX AU", 2.50, currency_code="AUD")
        cash = Cash("GBP")
        with pytest.raises(TypeError):
            portfolio.trade(None, units=1)
        with pytest.raises(TypeError):
            portfolio.trade(stock, units="1")
        with pytest.raises(TypeError):
            portfolio.trade(cash, units="1")

        stock.price = None
        with pytest.raises(ValueError):
            # cannot calculate consideration with a None value
            portfolio.trade(stock, units=1)

        # consideration must be numeric
        with pytest.raises(TypeError):
            portfolio.trade(stock, units=1, consideration="123")

        # codes such as 'AUD', 'USD', 'GBP'
        # are reserved for cash and shouldn't be used for other assets.
        stock = Stock("EUR", 2.50, currency_code="EUR")
        with pytest.raises(TypeError):
            portfolio.trade(stock, units=1)

    def test_portfolio_str(self):
        portfolio = self.portfolio
        assert str(portfolio) == "Portfolio('AUD')"

        self.audusd.rate = 0.7
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

    def test_portfolio_weight(self):
        Portfolio.reset()
        portfolio = Portfolio("USD")
        stock1 = Stock("ABC US", 2.00, currency_code="USD")
        stock2 = Stock("DEF US", 2.00, currency_code="USD")
        cash = self.usd
        portfolio.transfer(stock1, 100)
        portfolio.transfer(stock2, 100)
        assert portfolio.get_holding_weight("ABC US") == 0.5
        assert portfolio.get_holding_weight("DEF US") == 0.5

        portfolio.transfer(cash, 400)
        assert portfolio.get_holding_weight("USD") == 0.5
        assert portfolio.get_holding_weight("ABC US") == 0.25
        assert portfolio.get_holding_weight("DEF US") == 0.25
        assert portfolio.get_holding_weight("NOT A CODE") == 0

    def test_portfolio_compliance(self):
        Portfolio.reset()
        portfolio = Portfolio("USD")
        compliance = portfolio.compliance
        assert isinstance(compliance, Compliance)
        new_compliance = Compliance()
        portfolio.compliance = new_compliance
        assert portfolio.compliance is new_compliance
        with pytest.raises(TypeError):
            portfolio.compliance = None

    def test_portfolio_broker(self):
        Portfolio.reset()
        portfolio = Portfolio("USD")
        broker = portfolio.broker
        assert isinstance(broker, Broker)
        new_broker = Broker()
        portfolio.broker = new_broker
        assert portfolio.broker is new_broker
        with pytest.raises(TypeError):
            portfolio.broker = None
