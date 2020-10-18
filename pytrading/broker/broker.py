"""
A broker will execute some trade for a fee.
Charges and execution are organised as strategy patterns.
"""
import pytrading
from .charges import NoCharges
from .execution import FillAtLast


class Broker:
    def __init__(
        self,
        *,
        execution_strategy=FillAtLast(),
        charges_strategy=NoCharges(),
    ):
        self._execution_strategy = execution_strategy
        self._charges_strategy = charges_strategy

    def execute(self, trade):
        """ Apply some charge and execution strategy to the trade. """
        if not isinstance(trade, pytrading.Trade):
            raise TypeError("Expecting Trade instance.")
        self._charges_strategy.charge(trade)
        self._execution_strategy.execute(trade)
