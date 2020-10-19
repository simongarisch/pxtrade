import pytest
from pxtrade.assets.fx_rates import FxRate, validate_pair


def test_validate_pair():
    assert "AUDUSD" == validate_pair("AUDUSD")
    with pytest.raises(TypeError):
        validate_pair(123)
    with pytest.raises(ValueError):
        validate_pair("XXXYY")


def test_fx_rate_init():
    fx = FxRate("AUDUSD", 0.70)
    assert fx.pair == "AUDUSD"
    assert fx.rate == 0.70


def test_fx_rate_positive():
    fx = FxRate("AUDUSD", 0.70)
    assert fx.rate == 0.70
    fx.rate = 0.75
    assert fx.rate == 0.75
    with pytest.raises(ValueError):
        fx.rate = -0.85
    assert fx.rate == 0.75


def test_fx_currency_pair_read_only():
    fx = FxRate("AUDUSD", 0.70)
    with pytest.raises(AttributeError):
        fx.pair = "AUDAUD"


def test_fx_rate_get():
    with pytest.raises(ValueError):
        FxRate.get("AUDUSD")  # not available

    fx = FxRate("AUDUSD", 0.65)
    assert FxRate.get("AUDUSD") == 0.65

    fx.rate = 0.75
    assert FxRate.get("AUDUSD") == 0.75


def test_already_created():
    """Once a rate is created we must not create it again.
    We don't want multiple objects with different
    prices representing the same asset.
    """
    audusd = FxRate("AUDUSD", 0.65)
    assert audusd.rate == 0.65
    with pytest.raises(ValueError):
        FxRate("AUDUSD", 0.75)
    assert audusd.rate == 0.65


def test_observable():
    audusd = FxRate("AUDUSD", 0.65)

    class UsdCash:
        def __init__(self):
            self.local_value = 1.0
            self.update_aud_value()

        def update_aud_value(self):
            rate = FxRate.get("AUDUSD")
            self.aud_value = 1 / rate

        def observable_update(self, observable):
            self.update_aud_value()

    usd_cash = UsdCash()
    assert usd_cash.aud_value == 1 / 0.65
    audusd.add_observer(usd_cash)

    audusd.rate = 0.7
    assert usd_cash.aud_value == 1 / 0.7


def test_get_rate():
    audusd = FxRate("AUDUSD", 0.5)
    assert FxRate.get("AUDUSD") == 0.5
    assert FxRate.get("USDAUD") == 2.0
    audusd.rate = 0.8
    assert FxRate.get("AUDUSD") == 0.8
    assert FxRate.get("USDAUD") == 1.25
    with pytest.raises(TypeError):
        audusd.rate = "123"


def test_get_instance():
    audusd = FxRate("AUDUSD", 0.5)
    instance = FxRate.get_instance("AUDUSD")
    assert audusd is instance

    with pytest.raises(ValueError):
        FxRate.get_instance("USDAUD")


def test_get_observable_instance():
    audusd = FxRate("AUDUSD", 0.5)
    instance = FxRate.get_observable_instance("AUDUSD")
    assert instance is audusd

    instance = FxRate.get_observable_instance("USDAUD")
    assert instance is audusd
    with pytest.raises(ValueError):
        FxRate.get_observable_instance("XXXYYY")  # not available


def test_inverse_pair_creation():
    """Once we have created AUDUSD, for example,
    we cannot create USDAUD.
    """
    audusd = FxRate("AUDUSD", 0.5)
    assert audusd.rate == 0.5
    with pytest.raises(ValueError):
        FxRate("AUDUSD", 0.5)

    with pytest.raises(ValueError):
        FxRate("USDAUD", 2.0)
