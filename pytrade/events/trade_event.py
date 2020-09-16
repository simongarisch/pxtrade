from .base import AbstractEvent
from ..trade import Trade


class TradeEvent(AbstractEvent):
    def _validate(self, event_value):
        if not isinstance(event_value, Trade):
            raise TypeError("Expecting Trade instance.")

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
