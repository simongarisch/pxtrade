"""
Events such as changes in asset prices, fx rates and indicators will occur.
All events must define methods _validate, _process, __str__.
Events can only be processed once and will be associated with some backtest.
"""
from abc import ABC, abstractmethod
from ..util import to_datetime


class AbstractEvent(ABC):
    def __init__(self, datetime, event_value):
        self._datetime = to_datetime(datetime)
        self._validate(event_value)
        self._event_value = event_value
        self._processed = False

    def process(self):
        if self._processed is True:
            raise ValueError("Event has already been processed.")
        self._process()
        self._processed = True

    @property
    def datetime(self):
        return self._datetime

    @property
    def event_value(self):
        return self._event_value

    @property
    def processed(self):
        return self._processed

    @abstractmethod
    def _validate(self, event_value):
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def _process(self):
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def __str__(self):
        raise NotImplementedError()  # pragma: no cover
