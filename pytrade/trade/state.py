from enum import Enum


class TradeState(Enum):
    Proposed = 1
    FailedCompliance = 2
    PassedCompliance = 3
    SentForExecution = 4
    PartiallyFilled = 5
    Filled = 6
    Cancelled = 7
