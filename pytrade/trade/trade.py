""" Defines a proposed trade. """
from typing import Union
from pytrade.assets import Asset, Portfolio
from .state import TradeState


def _check_asset(asset: Union[Asset, str]):
    """ If an asset is passed then return this asset.
        However, if an asset code is passed make sure this is valid.
    """
    if isinstance(asset, Asset):
        return asset
    asset_code = asset
    if not isinstance(asset_code, str):
        raise TypeError("Expecting Asset instance or asset code.")
    asset = Asset.get_asset_for_code(asset_code)
    if asset is None:
        raise ValueError("Asset code '%s' doesn't exist." % asset_code)
    return asset


class Trade:
    def __init__(self, portfolio, asset, units):
        if not isinstance(portfolio, Portfolio):
            raise TypeError("Expecting a Portfolio instance.")
        if not isinstance(units, int):
            raise TypeError("Units for trade must be an integer.")
        self._portfolio = portfolio
        asset = self._asset = _check_asset(asset)
        self._asset_code = asset.code
        self._status = TradeState.Proposed
        self._passed_compliance = False
        self._units = units
        self._done = 0

    @property
    def portfolio(self):
        return self._portfolio

    @property
    def asset(self):
        return self._asset

    @property
    def asset_code(self):
        return self._asset_code

    @property
    def units(self):
        return self._units

    @property
    def done(self):
        return self._done

    @property
    def status(self):
        return self._status

    @property
    def passed_compliance(self):
        return self._passed_compliance

    def __str__(self):
        return (
            self.__class__.__name__
            + "("
            + "Portfolio('%s')" % self._portfolio.base_currency_code
            + ", '" + self._asset_code + "', "
            + str(self._units)
            + ")"
        )
