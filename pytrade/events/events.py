from enum import Enum


class EventType(Enum):
    AssetPriceEvent = 1
    FxRateEvent = 2
    IndicatorEvent = 3
