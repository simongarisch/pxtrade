""" A portfolio represents a collection of assets that'll
    be valued in some base currency.
"""
from collections import defaultdict
from numbers import Real
from .asset import Asset
from .cash import Cash
from .codes import check_currency_code
from .fx_rates import FxRate
from ..observable import Observer
from ..settings import get_default_currency_code


class Portfolio(Observer):
    """ A portfolio will observe the assets it holds. """
    def __init__(self, base_currency=None):
        super().__init__()
        if base_currency is None:
            base_currency = get_default_currency_code()
        base_currency = check_currency_code(base_currency)
        self._base_currency = base_currency
        self._holdings = defaultdict(lambda: 0)
        self._value = 0

    @property
    def value(self):
        """ value is read only. """
        return self._value

    def transfer(self, asset, units):
        self._holdings[asset] += units
        self._revalue()

    def trade(self, asset, units, consideration=None):
        if consideration is None:
            asset_local_value = asset.local_value
            if asset_local_value is None:
                raise ValueError("Asset local value is None.")
            consideration = asset.local_value * -units

        if not isinstance(consideration, Real):
            raise TypeError("Expecting numeric consideration.")

        currency_code = asset.currency_code
        cash = Asset.get_asset_for_code(currency_code)
        if cash is not None:
            if not isinstance(cash, Cash):
                raise TypeError(
                    "Currency code '%s' is reserved for cash." % currency_code
                )
        else:
            cash = Cash(currency_code)
        self._holdings[asset] += units
        self._holdings[cash] += consideration

    def observable_update(self):
        self._revalue()

    def _revalue(self):
        value = 0
        base_currency = self._base_currency
        for asset, units in self._holdings.items():
            fx_pair = base_currency + asset.currency_code
            fx_rate = FxRate.get(fx_pair)
            value += asset.local_value * fx_rate * units
        self._value = value
