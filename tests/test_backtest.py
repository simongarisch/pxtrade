from datetime import datetime
from pytrade.backtest import Backtest
from pytrade.events import IndicatorEvent


def test_backtest_indicator():
    backtest = Backtest()
    event = IndicatorEvent(
        "VIX", datetime(2020, 9, 1), 25,
        backtest=backtest,
    )
    assert backtest.get_indicator("VIX") is None
    backtest._process_event(event)
    assert backtest.get_indicator("VIX") == 25
