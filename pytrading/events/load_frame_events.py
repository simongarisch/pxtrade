import inspect
import pandas as pd
from .base import AbstractEvent
import pytrading
from pytrading.util import to_datetime


def load_frame_events(
    instance,
    df: pd.DataFrame,
    column: str,
    *,
    backtest,
    event_class,
) -> int:
    """ Loads backtest events from a data frame.
        Returns the number of events loaded.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Expecting pd.DataFrame instance.")
    if not isinstance(column, str):
        raise TypeError("Expecting string.")
    if not isinstance(backtest, pytrading.backtest.Backtest):
        raise TypeError("Expecting Backtest instance.")
    if not inspect.isclass(event_class):
        raise TypeError("Expecting Event class.")
    if not issubclass(event_class, AbstractEvent):
        raise TypeError("Expecting Event class.")

    if len(df.index) == 0:
        return 0  # nothing to load

    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("Expecting a datetime index.")

    series = df[column]
    event_count = 0
    for event_datetime, event_value in series.items():
        event_datetime = to_datetime(event_datetime)
        event = event_class(
            instance,
            event_datetime,
            event_value,
            backtest=backtest,
        )
        backtest.load_event(event)
        event_count += 1

    return event_count
