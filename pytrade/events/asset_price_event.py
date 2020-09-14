from .base import AbstractEvent
from ..util import check_positive_numeric


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
