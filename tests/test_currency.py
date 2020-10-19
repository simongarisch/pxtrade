import pytest
from pxtrade.assets import reset, Asset, Cash


def test_cash_code():
    reset()
    aud = Cash("AUD")
    assert isinstance(aud, Asset)
    assert aud.currency_code == "AUD"
    assert aud.price == 1
    assert aud.local_value == 1


def test_cannot_change_price():
    reset()
    aud = Cash("AUD")
    with pytest.raises(AttributeError):
        aud.price = 2
