import pytest
from pytrade.assets.asset import Asset
from pytrade.assets.cash import Cash


def get_aud():
    aud = Asset.get_asset_for_code("AUD")
    if aud is None:
        aud = Cash("AUD")
    return aud


def test_cash_code():
    aud = get_aud()
    assert isinstance(aud, Asset)
    assert aud.currency_code == "AUD"
    assert aud.price == 1
    assert aud.local_value == 1


def test_cannot_change_price():
    aud = get_aud()
    with pytest.raises(AttributeError):
        aud.price = 2
