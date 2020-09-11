from abc import ABC, abstractmethod
from ..util import check_positive_numeric, to_datetime
from ..assets.fx_rates import FxRate
from ..trade import ProposedTrade


class AbstractEvent(ABC):
    def __init__(self, datetime, event_value):
        self._datetime = to_datetime(datetime)
        self._validate(event_value)
        self._event_value = event_value

    @property
    def datetime(self):
        return self._datetime

    @property
    def event_value(self):
        return self._event_value

    @abstractmethod
    def _validate(self, event_value):
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


class ProposedTradeEvent(AbstractEvent):
    def _validate(self, event_value):
        if not isinstance(event_value, ProposedTrade):
            raise TypeError("Expecting ProposedTrade instance.")


class IndicatorEvent(AbstractEvent):
    def __init__(self, datetime, event_value, *, validation_func=None):
        if validation_func is not None:
            if not callable(validation_func):
                raise TypeError("Expecting a callable object.")

        self._validation_func = validation_func
        super().__init__(datetime, event_value)

    def _validate(self, event_value):
        if self._validation_func is not None:
            self._validation_func(event_value)
