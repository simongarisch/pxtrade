import pytest
from pytrade.assets import Stock, Portfolio
from pytrade.trade import ProposedTrade


class TestTrade(object):
    def setup_method(self, *args):
        portfolio = self.portfolio = Portfolio("AAA")
        self.stock = Stock("ZZB AU", 2.50, currency_code="AUD")
        self.proposed_trade = ProposedTrade(portfolio, "ZZB AU", 100)

    def teardown_method(self, *args):
        del self.stock
        del self.portfolio
        del self.proposed_trade

    def test_proposed_trade_init(self):
        proposed_trade = self.proposed_trade
        assert proposed_trade.portfolio is self.portfolio
        assert proposed_trade.asset is self.stock
        assert proposed_trade.asset_code == "ZZB AU"
        assert proposed_trade.units == 100

    def test_proposed_trade_init_with_asset(self):
        proposed_trade = ProposedTrade(
            self.portfolio, self.stock, 300,
        )
        assert proposed_trade.portfolio is self.portfolio
        assert proposed_trade.asset is self.stock
        assert proposed_trade.asset_code == "ZZB AU"
        assert proposed_trade.units == 300
        with pytest.raises(TypeError):
            ProposedTrade(123, 100)

    def test_proposed_trade_immutable(self):
        proposed_trade = self.proposed_trade
        with pytest.raises(AttributeError):
            proposed_trade.portfolio = self.portfolio
        with pytest.raises(AttributeError):
            proposed_trade.asset = self.stock
        with pytest.raises(AttributeError):
            proposed_trade.asset_code = "ZZB AU"
        with pytest.raises(AttributeError):
            proposed_trade.units = 500

    def test_proposed_trade_no_asset(self):
        with pytest.raises(ValueError):
            ProposedTrade(
                self.portfolio, "NO_ASSET_WITH_THIS_CODE", 200
            )

    def test_units_must_be_int(self):
        with pytest.raises(TypeError):
            ProposedTrade(
                self.portfolio, "ZZB AU", "100"
            )

    def test_trade_str(self):
        tradestr = str(self.proposed_trade)
        print(tradestr)
        assert tradestr == "ProposedTrade(Portfolio('AAA'), 'ZZB AU', 100)"
