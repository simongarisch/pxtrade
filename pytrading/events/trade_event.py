from .base import AbstractEvent
from pytrading.trade import Trade, trade_pipeline


class TradeEvent(AbstractEvent):
    def _validate(self, event_value):
        if not isinstance(event_value, Trade):
            raise TypeError("Expecting Trade instance.")

    def _process(self):
        trade = self._event_value
        trade_pipeline.run(trade)

    def __str__(self):
        return (
            self.__class__.__name__
            + "("
            + str(self._datetime)
            + ", "
            + str(self._event_value)
            + ")"
        )
