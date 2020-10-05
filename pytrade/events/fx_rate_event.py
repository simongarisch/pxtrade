from .base import AbstractEvent
from ..assets.fx_rates import FxRate
from ..util import check_positive_numeric


class FxRateEvent(AbstractEvent):
    def __init__(self, fx_rate, datetime, event_value, **kwargs):
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
