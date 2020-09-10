import pytest
from pytrade.util import (
    clean_string,
    check_positive_numeric,
)


def test_clean_string():
    assert clean_string("XXX") == "XXX"
    assert clean_string(" XxX ") == "XXX"
    assert clean_string(" x") == "X"


def test_check_positive_numeric():
    assert check_positive_numeric(12) == 12
    assert check_positive_numeric(1.1) == 1.1
    assert check_positive_numeric(0) == 0
    with pytest.raises(TypeError):
        check_positive_numeric("xxx")
    with pytest.raises(ValueError):
        check_positive_numeric(-1.1)
