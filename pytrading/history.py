"""
We'll want to keep a history of all assets,
prices and portfolio positions for backtesting.
Here we keep this history in a data frame and visit
different objects to record their status.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from weakref import WeakSet
import pandas as pd
import pytrading
from pytrading.assets import Asset, FxRate, Portfolio


class Visitor(ABC):
    """ Our history instance can visit different objects
        and record data relating to them.
    """
    @abstractmethod
    def visit(self, instance):
        raise NotImplementedError()  # pragma: no cover


class AssetVisitor(Visitor):
    def visit(self, instance):
        return [(instance.code, instance.local_value)]


class FxRateVisitor(Visitor):
    def visit(self, instance):
        return [(instance.pair, instance.rate)]


class PortfolioVisitor(Visitor):
    def visit(self, instance):
        portfolio = instance
        portfolio_code = portfolio.code

        rows = []
        rows.append((portfolio_code, portfolio.value))
        for asset in Asset.get_instances():
            asset_code = asset.code
            rows.append((
                portfolio_code + "_" + asset_code,
                portfolio.get_holding_units(asset_code)
            ))
        return rows


class History:
    instances = WeakSet()

    def __init__(self, portfolios, *, backtest=None):
        self.instances.add(self)
        self._history = pd.DataFrame()
        self._asset_visitor = AssetVisitor()
        self._fx_rate_visitor = FxRateVisitor()
        self._portfolio_visitor = PortfolioVisitor()

        if isinstance(portfolios, Portfolio):
            portfolios = [portfolios]

        if not isinstance(portfolios, list):
            raise TypeError("Expecting portfolio or list of portfolios.")

        for portfolio in portfolios:
            if not isinstance(portfolio, Portfolio):
                raise TypeError("Expecting Portfolio instance.")

        if backtest is not None:
            if not isinstance(backtest, pytrading.backtest.Backtest):
                raise TypeError("Expecting Backtest instance.")

        self._portfolios = portfolios
        self._backtest = backtest

    def _get_visitor(self, instance):
        if isinstance(instance, Asset):
            return self._asset_visitor
        if isinstance(instance, FxRate):
            return self._fx_rate_visitor
        if isinstance(instance, Portfolio):
            return self._portfolio_visitor
        raise NotImplementedError(
            "Unable to record history for " + instance.__class__.__name__
        )

    def take_snapshot(self, date_time):
        if not isinstance(date_time, datetime):
            raise TypeError("Expecting datetime instance.")
        instances = list()
        instances.extend(Asset.get_instances())
        instances.extend(FxRate.get_instances())
        instances.extend(self._portfolios)

        get_visitor = self._get_visitor
        snapshot = pd.Series(dtype=object)
        snapshot.name = date_time
        for instance in instances:
            visitor = get_visitor(instance)
            rows = visitor.visit(instance)
            for row in rows:
                name, value = row
                snapshot[name] = value

        backtest = self._backtest
        if backtest is not None:
            for key, value in backtest.indicators.items():
                snapshot[key] = value

        self._history = self._history.append(snapshot)

    def get(self):
        return self._history.copy()
