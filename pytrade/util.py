from numbers import Real
from datetime import datetime
from datetime import date as datetime_date
from copy import deepcopy
import pandas as pd
import numpy as np


def clean_string(s: str) -> str:
    """ Cleans and returns an input string
    >>> clean_string(" xYz ")
    'XYZ'
    """
    return str(s).strip().upper()


def clean_column_name(column):
    """ Cleans and returns a dataframe column name.
    >>> clean_column_name("Adj Close")
    'adj_close'
    """
    return str(column).strip().lower().replace(" ", "_")


def check_positive_numeric(x):
    """ Check that some value is both numeric and >= 0
        before returning it.
    """
    if not isinstance(x, Real):
        raise TypeError("Expecting numeric value.")
    if x < 0:
        raise ValueError("Value must be >= 0")
    return x


def to_datetime(t):
    """ Convert some object representing a datetime
        to a Python datetime object. Often times are represented as
        np.datetime64 or pd.Timestamp objects.
    """
    if isinstance(t, pd.Timestamp):
        return t.to_pydatetime()
    if isinstance(t, np.datetime64):
        return pd.Timestamp(t).to_pydatetime()
    if isinstance(t, datetime):
        return t
    if isinstance(t, datetime_date):
        return datetime.combine(t, datetime.min.time())
    raise TypeError("Unrecognised time object: " + str(t))


def memento(obj):
    """ A memento pattern to restore objects. """
    state = deepcopy(obj.__dict__)

    def restore():
        obj.__dict__.clear()
        obj.__dict__.update(state)

    return restore
