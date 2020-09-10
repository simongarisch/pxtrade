import pytest
from datetime import datetime
import pandas as pd
import numpy as np
from pytrade.util import (
    clean_string,
    check_positive_numeric,
    to_datetime,
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


def test_to_datetime():
    dt = datetime(2020, 9, 10, 12, 30)
    assert to_datetime(dt) is dt
    assert to_datetime(np.datetime64(dt)) == dt
    assert to_datetime(pd.Timestamp(dt)) == dt
    with pytest.raises(TypeError):
        to_datetime("xxx")
