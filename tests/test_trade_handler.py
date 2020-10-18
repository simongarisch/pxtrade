import pytest
from pytrading.assets import reset, Stock, Portfolio
from pytrading.trade import Trade, trade_pipeline
from pytrading.trade.trade_pipeline import Handler


class CustomHandler(Handler):
    handled = False

    def handle(self, trade):
        self.handled = True


class TestTrade(object):
    def setup_method(self, *args):
        reset()
        portfolio = self.portfolio = Portfolio("AUD")
        self.stock = Stock("ZZB AU", 2.50, currency_code="AUD")
        self.trade = Trade(portfolio, "ZZB AU", 100)

    def teardown_method(self, *args):
        del self.portfolio
        del self.trade
        del self.stock

    def test_handler_types(self):
        with pytest.raises(TypeError):
            trade_pipeline.run(None)  # requires Trade instance

        with pytest.raises(TypeError):
            CustomHandler().set_next(123)

    def test_create_pipeline(self):
        handler1 = CustomHandler()
        handler2 = CustomHandler()
        handler3 = CustomHandler()
        handler1.set_next(handler2).set_next(handler3)
        assert handler1.handled is False
        assert handler2.handled is False
        assert handler3.handled is False
        handler1.run(self.trade)
        assert handler1.handled is True
        assert handler2.handled is True
        assert handler3.handled is True
