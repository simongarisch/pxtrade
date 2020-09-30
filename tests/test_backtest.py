from datetime import datetime
import pytest
import pytrade
from pytrade.assets import Stock, Portfolio
from pytrade.backtest import Backtest
from pytrade.strategy import Strategy
from pytrade.events import AssetPriceEvent, IndicatorEvent


def test_backtest_indicator():
    backtest = Backtest()
    event = IndicatorEvent(
        "VIX", datetime(2020, 9, 1), 25,
        backtest=backtest,
    )
    backtest.load_event(event)
    assert backtest.get_indicator("VIX") is None
    backtest.run()
    assert backtest.get_indicator("VIX") == 25


def test_backtest_num_events_loaded():
    stock = Stock("TTT AU", 2.50)
    events = [
        AssetPriceEvent(stock, datetime(2020, 9, 1), 2.50),
        AssetPriceEvent(stock, datetime(2020, 9, 2), 2.60),
        AssetPriceEvent(stock, datetime(2020, 9, 3), 2.70),
    ]
    backtest = Backtest()
    [backtest.load_event(event) for event in events]
    assert backtest.num_events_loaded == 3
    backtest.run()
    assert stock.price == 2.70
    assert backtest.num_events_loaded == 0


def test_backtest_strategy():
    with pytest.raises(TypeError):
        Backtest(strategy="Strategy")

    portfolio = Portfolio("AUD")
    stock = Stock("HHH AU", 2.50, currency_code="AUD")
    events = [
        AssetPriceEvent(stock, datetime(2020, 9, 1), 2.50),
        AssetPriceEvent(stock, datetime(2020, 9, 2), 2.60),
        AssetPriceEvent(stock, datetime(2020, 9, 3), 2.70),
    ]

    class BasicStrategy(Strategy):
        def generate_trades(self):
            # always buy 1 share of 'HHH AU'
            return pytrade.Trade(portfolio, stock, 1)

    backtest = Backtest(BasicStrategy())
    [backtest.load_event(event) for event in events]
    backtest.run()
    assert portfolio.get_holding_units("HHH AU") == 3
    assert portfolio.get_holding_units("AUD") == -(2.50 + 2.60 + 2.70)
