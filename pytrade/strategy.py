"""
Defines a strategy for our backtest.
Each strategy will return trades to be executed.
"""
from abc import ABC, abstractmethod
from typing import Union, List
from pytrade import trade


class Strategy(ABC):
    @abstractmethod
    def generate_trades(self) -> Union[None, trade.Trade, List[trade.Trade]]:
        raise NotImplementedError
