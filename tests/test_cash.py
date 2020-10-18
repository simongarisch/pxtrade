from pytrading.assets import reset, Cash


def test_cash():
    reset()
    aud = Cash("AUD")
    assert aud.code == "AUD"
    assert aud.currency_code == "AUD"
    assert aud.local_value == 1.0
    assert aud.multiplier == 1.0
