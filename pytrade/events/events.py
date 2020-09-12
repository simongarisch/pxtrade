"""
Events such as changes in asset prices, fx rates and indicators will occur.
All events must define methods _validate, _process, __str__.
Events can only be processed once.
"""
from abc import ABC, abstractmethod
from ..util import check_positive_numeric, to_datetime
from ..assets.fx_rates import FxRate
from ..trade import ProposedTrade


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

    @abstractmethod
    def _validate(self, event_value):
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def _process(self):
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def __str__(self):
        raise NotImplementedError()  # pragma: no cover


class AssetPriceEvent(AbstractEvent):
    def __init__(self, asset, datetime, event_value):
        super().__init__(datetime, event_value)
        self._asset = asset

    @property
    def asset(self):
        return self._asset

    def _validate(self, event_value):
        check_positive_numeric(event_value)

    def _process(self):
        self._asset.price = self._event_value

    def __str__(self):
        return (
            self.__class__.__name__
            + "("
            + self._asset.__class__.__name__
            + "('" + self._asset.code + "')"
            + ", "
            + str(self._datetime)
            + ", "
            + str(self._event_value)
            + ")"
        )


class FxRateEvent(AbstractEvent):
    def __init__(self, fx_rate, datetime, event_value):
        super().__init__(datetime, event_value)
        if not isinstance(fx_rate, FxRate):
            raise TypeError("Expecting FxRate instance.")
        self._fx_rate = fx_rate

    @property
    def fx_rate(self):
        return self._fx_rate

    def _validate(self, event_value):
        check_positive_numeric(event_value)

    def _process(self):
        self._fx_rate.rate = self._event_value

    def __str__(self):
        return (
            self.__class__.__name__
            + "('"
            + str(self._fx_rate)
            + "', "
            + str(self._datetime)
            + ", "
            + str(self._event_value)
            + ")"
        )


class ProposedTradeEvent(AbstractEvent):
    def _validate(self, event_value):
        if not isinstance(event_value, ProposedTrade):
            raise TypeError("Expecting ProposedTrade instance.")

    def _process(self):
        pass  # TODO

    def __str__(self):
        return (
            self.__class__.__name__
            + "("
            + str(self._datetime)
            + ", "
            + str(self._event_value)
            + ")"
        )


class IndicatorEvent(AbstractEvent):
    def __init__(
        self,
        indicator_name,
        datetime,
        event_value,
        *,
        validation_func=None,
    ):
        if not isinstance(indicator_name, str):
            raise TypeError("Expecting string.")
        if validation_func is not None:
            if not callable(validation_func):
                raise TypeError("Expecting a callable object.")

        self._indicator_name = indicator_name
        self._validation_func = validation_func
        super().__init__(datetime, event_value)

    @property
    def indicator_name(self):
        return self._indicator_name

    def _validate(self, event_value):
        if self._validation_func is not None:
            self._validation_func(event_value)

    def _process(self):
        pass  # TODO

    def __str__(self):
        return (
            self.__class__.__name__
            + "('"
            + str(self._indicator_name)
            + "', "
            + str(self._datetime)
            + ", "
            + str(self._event_value)
            + ")"
        )
