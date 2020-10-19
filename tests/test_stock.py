from pxtrade.assets import Stock


def test_stock_str():
    stock = Stock("QQQ AU", 2.55, currency_code="AUD")
    stock_str = str(stock)
    assert stock_str == "Stock('QQQ AU', 2.55, currency_code='AUD')"
