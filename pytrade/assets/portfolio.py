"""
A portfolio represents a collection of assets that'll be valued
in some base currency.
Whenever an asset is transfered to / from or traded into the portfolio
the revalue method is called.
"""
from collections import defaultdict
from numbers import Real
from .asset import Asset, VariablePriceAsset
from .cash import Cash
from .codes import check_currency_code
from .fx_rates import FxRate, is_equivalent_pair
from ..observable import Observer
from ..settings import get_default_currency_code


class Portfolio(Observer):
    """ A portfolio will observe the assets it holds. """
    def __init__(self, base_currency_code=None):
        super().__init__()
        if base_currency_code is None:
            base_currency_code = get_default_currency_code()
        base_currency_code = check_currency_code(base_currency_code)
        self._base_currency_code = base_currency_code
        self._holdings = defaultdict(lambda: 0)
        self._value = 0

    @property
    def value(self):
        """ value is read only after init. """
        return self._value

    @property
    def base_currency_code(self):
        """ base_currency_code is read only after init. """
        return self._base_currency_code

    def transfer(self, asset, units):
        self._holdings[asset] += units
        self._revalue()

    def trade(self, asset, units, consideration=None):
        if not isinstance(asset, Asset):
            raise TypeError("Expecting Asset instance.")
        if not isinstance(units, int):
            raise TypeError("Expecting int.")

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
        self._revalue()

    def observable_update(self, observable):
        self._revalue()

    def _revalue(self):
        value = 0
        base_currency_code = self._base_currency_code
        for asset, units in self._holdings.items():
            # make sure to observe all assets held and the currencies they
            # are quoted in.
            fx_pair = base_currency_code + asset.currency_code
            if not is_equivalent_pair(fx_pair):
                fx_observable = FxRate.get_observable_instance(fx_pair)
                fx_observable.add_observer(self)
            if isinstance(asset, VariablePriceAsset):
                asset.add_observer(self)

            # calculate the value of this holding to the portfolio
            fx_rate = FxRate.get(fx_pair)
            value += asset.local_value / fx_rate * units
        self._value = value

    def __str__(self):
        return "Portfolio(%s): \n" % self.base_currency_code + "\n".join(
            [
                str(asset) + ": " + format(int(units), ",d")
                for asset, units in self._holdings.items()
            ]
        )
