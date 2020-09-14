from datetime import datetime
from pytrade.assets import Stock
from pytrade.backtest import Backtest
from pytrade.events import AssetPriceEvent, IndicatorEvent


def test_backtest_indicator():
    backtest = Backtest()
    event = IndicatorEvent(
        "VIX", datetime(2020, 9, 1), 25,
        backtest=backtest,
    )
    backtest.load_event(event)
    assert backtest.get_indicator("VIX") is None
    backtest.process_events()
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
    backtest.process_events()
    assert stock.price == 2.70
