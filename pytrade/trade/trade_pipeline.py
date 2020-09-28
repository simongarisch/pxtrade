"""
Each trade needs to go through a sequence of steps before being sent
for execution. Trade creation -> run compliance -> execution.
"""
from abc import ABC, abstractmethod
from pytrade.trade import Trade
from pytrade.util import memento


class Handler(ABC):
    """ A chain of responsibility pattern for the trade pipeline. """
    _next = None

    def set_next(self, handler):
        if not isinstance(handler, Handler):
            raise TypeError("Expecting Handler instance.")
        self._next = handler
        return handler

    def run(self, trade):
        if not isinstance(trade, Trade):
            raise TypeError("Expecting Trade instance.")
        self.handle(trade)
        if self._next is not None:
            self._next.run(trade)

    @abstractmethod
    def handle(self, trade):
        raise NotImplementedError  # pragma: no cover


class ComplianceHandler(Handler):
    """
    Compliance is run on the portfolio assuming that the trade is executed.
    The portfolio is then rolled back using the memento pattern once this
    check is complete.
    """
    def handle(self, trade):
        portfolio = trade.portfolio
        compliance = portfolio.compliance
        restore_portfolio = memento(portfolio)

        trade.execute()
        trade.passes_compliance = compliance.passes(portfolio)
        restore_portfolio()


class ExecutionHandler(Handler):
    def handle(self, trade):
        trade.execute()


def make_trade_pipeline():
    compliance_handler = ComplianceHandler()
    execution_handler = ExecutionHandler()

    compliance_handler.set_next(execution_handler)
    return compliance_handler


trade_pipeline = make_trade_pipeline()  # singleton
