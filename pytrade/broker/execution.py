""" A strategy pattern for trade execution. """
from abc import ABC, abstractmethod
from numbers import Real


class AbstractExecution(ABC):
    @abstractmethod
    def execute(self, trade):
        raise NotImplementedError()  # pragma: no cover


class FillAtLast(AbstractExecution):
    def execute(self, trade):
        asset = trade.asset
        portfolio = trade.portfolio
        units = trade.units
        portfolio.trade(asset, units)


class FillAtLastWithSlippage(AbstractExecution):
    def __init__(self, slippage):
        super().__init__()
        if not isinstance(slippage, Real):
            raise TypeError("Expecting numeric value for slippage.")
        if slippage < 0 or slippage >= 1:
            raise ValueError("Expecting slippage between 0 and 1.")
        self._slippage = slippage

    def execute(self, trade):
        asset = trade.asset
        portfolio = trade.portfolio
        units = trade.units
        consideration = asset.local_value * -units
        if consideration > 0:
            # receive less cash when selling
            consideration *= (1 - self._slippage)
        if consideration < 0:
            # pay more cash when buying
            consideration *= (1 + self._slippage)
        portfolio.trade(asset, units, consideration=consideration)
