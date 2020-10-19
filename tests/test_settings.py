from configparser import ConfigParser
from pxtrade.assets.codes import check_currency_code
from pxtrade.settings import (
    config,
    set_default_currency_code,
    get_default_currency_code,
)


def test_settings():
    assert isinstance(config, ConfigParser)
    ticker = config["currency"]["default"]
    check_currency_code(ticker)


def test_set_default_currency_code():
    set_default_currency_code("XXX")
    assert get_default_currency_code() == "XXX"
    set_default_currency_code("YYY")
    assert get_default_currency_code() == "YYY"
