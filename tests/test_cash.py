from pytrade.assets import Asset, Cash


def test_cash():
    aud = Asset.get_asset_for_code("AUD")
    if aud is None:
        aud = Cash("AUD")
    assert aud.code == "AUD"
    assert aud.currency_code == "AUD"
    assert aud.local_value == 1.0
    assert aud.multiplier == 1.0
