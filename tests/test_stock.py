from pytrade.assets import Stock


def test_stock_str():
    zzb = Stock("ZZB AU", 2.55, currency_code="AUD")
    zzb_str = str(zzb)
    assert zzb_str == "Stock('ZZB AU', 2.55, currency_code='AUD')"
