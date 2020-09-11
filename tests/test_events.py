import pytest
from datetime import datetime
from pytrade.assets import Stock, FxRate
from pytrade.trade import ProposedTrade
from pytrade.events.events import (
    AssetPriceEvent,
    FxRateEvent,
    ProposedTradeEvent,
    IndicatorEvent,
)


def test_asset_price_event():
    xyz = Stock("XYZ AU", 2.50, currency_code="AUD")
    dt = datetime(2020, 9, 1, 12, 30)
    event = AssetPriceEvent(xyz, dt, 2.60)
    assert event.asset is xyz
    assert event.datetime is dt
    assert event.event_value == 2.60

    # args must be of specific types / values
    with pytest.raises(TypeError):
        AssetPriceEvent(xyz, "2020-09-01", 2.60)
    with pytest.raises(TypeError):
        AssetPriceEvent(xyz, dt, "2.60")
    with pytest.raises(ValueError):
        AssetPriceEvent(xyz, dt, -2.0)  # must be positive

    # is immutable
    with pytest.raises(AttributeError):
        event.asset = xyz
    with pytest.raises(AttributeError):
        event.datetime = dt
    with pytest.raises(AttributeError):
        event.event_value = 2.65


def test_fx_rate_event():
    fx_rate = FxRate("AUDNZD")
    dt = datetime(2020, 9, 1, 12, 30)
    event = FxRateEvent(fx_rate, dt, 1.10)
    assert event.fx_rate is fx_rate
    assert event.fx_rate.pair == "AUDNZD"
    assert event.datetime is dt
    assert event.event_value == 1.10

    # args must be of specific types / values
    with pytest.raises(TypeError):
        FxRateEvent("AUDNZD", dt, 1.10)
    with pytest.raises(TypeError):
        FxRateEvent(fx_rate, "2020-09-01", 1.10)
    with pytest.raises(TypeError):
        FxRateEvent(fx_rate, dt, "1.10")

    # is immutable
    with pytest.raises(AttributeError):
        event.fx_rate = fx_rate
    with pytest.raises(AttributeError):
        event.datetime = dt
    with pytest.raises(AttributeError):
        event.event_value = 1.09


def test_proposed_trade_event():
    goog = Stock("GOOG US", 1500, currency_code="USD")
    dt = datetime(2020, 9, 1, 12, 30)
    proposed_trade = ProposedTrade(goog, +100)
    event = ProposedTradeEvent(dt, proposed_trade)
    assert event.datetime is dt
    assert event.event_value is proposed_trade

    # args must be of specific types / values
    with pytest.raises(TypeError):
        ProposedTradeEvent("2020-09-01", proposed_trade)
    with pytest.raises(TypeError):
        ProposedTradeEvent(dt, 100)

    # is immutable
    with pytest.raises(AttributeError):
        event.datetime = datetime
    with pytest.raises(AttributeError):
        event.event_value = proposed_trade


def test_indicator_event():
    dt = datetime(2020, 9, 1, 12, 30)
    event = IndicatorEvent(dt, "some_value")
    assert event.datetime is dt
    assert event.event_value == "some_value"

    # is immutable
    with pytest.raises(AttributeError):
        event.datetime = dt
    with pytest.raises(AttributeError):
        event.event_value = "some_value"


def test_indicator_event_validation():
    dt = datetime(2020, 9, 1, 12, 30)

    def validation_func(x):
        if not isinstance(x, str):
            raise TypeError("Expecting string.")

    event = IndicatorEvent(
        dt, "xxx", validation_func=validation_func
    )
    assert event.datetime is dt
    assert event.event_value == "xxx"

    # event value must pass valiadation_func validation
    with pytest.raises(TypeError):
        IndicatorEvent(
            dt, 123, validation_func=validation_func
        )

    # validation func must be callable
    with pytest.raises(TypeError):
        IndicatorEvent(
            dt, "xxx", validation_func=123
        )
