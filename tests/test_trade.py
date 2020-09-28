import pytest
from pytrade.assets import Stock, Portfolio
from pytrade.trade import Trade, TradeState


class TestTrade(object):
    def setup_method(self, *args):
        portfolio = self.portfolio = Portfolio("AAA")
        self.stock = Stock("ZZB AU", 2.50, currency_code="AUD")
        self.trade = Trade(portfolio, "ZZB AU", 100)

    def teardown_method(self, *args):
        del self.stock
        del self.portfolio
        del self.trade

    def test_proposed_trade_init(self):
        trade = self.trade
        assert trade.portfolio is self.portfolio
        assert trade.asset is self.stock
        assert trade.asset_code == "ZZB AU"
        assert trade.units == 100
        assert trade.status is TradeState.Proposed

    def test_passed_compliance(self):
        trade = self.trade
        assert trade.passed_compliance is False
        trade.passed_compliance = True
        assert trade.passed_compliance is True
        with pytest.raises(TypeError):
            trade.passed_compliance = 42

    def test_proposed_trade_init_with_asset(self):
        trade = Trade(
            self.portfolio, self.stock, 300,
        )
        assert trade.portfolio is self.portfolio
        assert trade.asset is self.stock
        assert trade.asset_code == "ZZB AU"
        assert trade.units == 300
        with pytest.raises(TypeError):
            Trade("Portfolio", self.stock, 100)
        with pytest.raises(TypeError):
            Trade(self.portfolio, 123, 100)

    def test_proposed_trade_immutable(self):
        trade = self.trade
        with pytest.raises(AttributeError):
            trade.portfolio = self.portfolio
        with pytest.raises(AttributeError):
            trade.asset = self.stock
        with pytest.raises(AttributeError):
            trade.asset_code = "ZZB AU"
        with pytest.raises(AttributeError):
            trade.units = 500

    def test_proposed_trade_no_asset(self):
        with pytest.raises(ValueError):
            Trade(
                self.portfolio, "NO_ASSET_WITH_THIS_CODE", 200
            )

    def test_units_must_be_int(self):
        with pytest.raises(TypeError):
            Trade(
                self.portfolio, "ZZB AU", "100"
            )

    def test_trade_str(self):
        tradestr = str(self.trade)
        print(tradestr)
        assert tradestr == "Trade(Portfolio('AAA'), 'ZZB AU', 100)"
