import pytest
from pytrading.assets.codes import (
    check_code,
    check_currency_code,
    Codes,
)


class Test:
    pass


def test_check_code():
    assert check_code("AAPL") == "AAPL"
    assert check_code(" aapl ") == "AAPL"
    with pytest.raises(TypeError):
        check_code(123)


def test_check_currency_code():
    assert check_currency_code("USD") == "USD"
    assert check_currency_code(" usd ") == "USD"
    with pytest.raises(TypeError):
        check_currency_code(123)
    with pytest.raises(ValueError):
        check_currency_code("XXXX")  # must be only 3 chars


def test_codes():
    codes = Codes()

    # there are no registered codes to start with
    assert len(codes.get_registered_codes()) == 0
    assert codes.code_in_use("XXX") is False
    assert codes.get_object_for_code("XXX") is None

    # add one code
    obj = Test()
    codes.register("XXX", obj)
    assert len(codes.get_registered_codes()) == 1
    assert codes.code_in_use("XXX") is True
    assert codes.get_object_for_code("XXX") is obj

    # check that this must be unique
    codes.register("XXX", obj)
    assert len(codes.get_registered_codes()) == 1

    obj2 = Test()
    with pytest.raises(ValueError):
        codes.register("XXX", obj2)

    # the objects are weakly referenced
    del obj
    assert len(codes.get_registered_codes()) == 0
