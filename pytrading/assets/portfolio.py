"""
A portfolio represents a collection of assets that'll be valued
in some base currency.
Whenever an asset is transfered to / from or traded into the portfolio
the revalue method is called.
"""
from collections import defaultdict
from numbers import Real
from .asset import Asset, VariablePriceAsset
from .cash import Cash, get_cash
from .codes import Codes, check_code, check_currency_code
from .fx_rates import FxRate, is_equivalent_pair
from ..observable import Observer
from ..settings import get_default_currency_code
from ..compliance import Compliance
from ..broker import Broker


class Portfolio(Observer):
    """ A portfolio will observe the assets it holds. """
    _codes = Codes()

    @classmethod
    def reset(cls):
        cls._codes.reset()

    def __init__(self, base_currency_code=None, *, code=None):
        super().__init__()
        if base_currency_code is None:
            base_currency_code = get_default_currency_code()
        if code is None:
            code = "Portfolio"
        # we can't have more than one portfolio with a code of None
        self._codes.register(code, self)
        self._base_currency_code = check_currency_code(base_currency_code)
        self._code = code
        self._holdings = defaultdict(lambda: 0)
        self._value = 0
        self._compliance = Compliance()  # empty by default
        self._broker = Broker()

    @property
    def value(self):
        """ value is read only after init. """
        return self._value

    @property
    def code(self):
        return self._code

    @property
    def base_currency_code(self):
        """ base_currency_code is read only after init. """
        return self._base_currency_code

    @property
    def compliance(self):
        return self._compliance

    @compliance.setter
    def compliance(self, compliance):
        if not isinstance(compliance, Compliance):
            raise TypeError("Expecting Compliance instance.")
        self._compliance = compliance

    @property
    def broker(self):
        return self._broker

    @broker.setter
    def broker(self, broker):
        if not isinstance(broker, Broker):
            raise TypeError("Expecting Broker instance.")
        self._broker = broker

    def transfer(self, asset, units):
        self.trade(asset, units, consideration=0)

    def trade(self, asset, units, consideration=None):
        if not isinstance(asset, Asset):
            raise TypeError("Expecting Asset instance.")
        if not isinstance(asset, Cash):
            # non-cash assets must be traded in whole units
            if not isinstance(units, int):
                raise TypeError("Expecting int.")
        else:
            if not isinstance(units, Real):
                raise TypeError("Expecting numeric value.")

        if consideration is None:
            asset_local_value = asset.local_value
            if asset_local_value is None:
                raise ValueError("Asset local value is None.")
            consideration = asset.local_value * -units

        if not isinstance(consideration, Real):
            raise TypeError("Expecting numeric consideration.")

        asset_currency_code = asset.currency_code
        cash = get_cash(asset_currency_code)
        if isinstance(asset, Cash):  # we are trading FX
            base_code = self._base_currency_code
            cash = get_cash(base_code)
            consideration /= FxRate.get(base_code + asset_currency_code)

        # print("asset: ", asset)
        # print("cash: ", cash)
        self._holdings[asset] += units
        self._holdings[cash] += consideration
        self._check_observable(asset)
        self._revalue()

    def _check_observable(self, asset):
        """ Check whether we need to observe some asset.
            If we have some non-zero holding then we should
            observe the asset and its quoted currency.
        """
        units = self._holdings[asset]
        fx_pair = self._base_currency_code + asset.currency_code
        if not is_equivalent_pair(fx_pair):  # e.g. don't observe 'AUDAUD'
            fx_observable = FxRate.get_observable_instance(fx_pair)
            fx_observable.add_observer(self)
        if isinstance(asset, VariablePriceAsset):
            if units != 0:
                asset.add_observer(self)
            else:
                asset.remove_observer(self)

    def observable_update(self, observable):
        self._revalue()

    def _revalue(self):
        value = 0
        base_currency_code = self._base_currency_code
        for asset, units in self._holdings.items():
            # calculate the value of this holding to the portfolio
            fx_pair = base_currency_code + asset.currency_code
            fx_rate = FxRate.get(fx_pair)
            value += asset.local_value / fx_rate * units
        self._value = value

    def get_holding_units(self, asset_code):
        asset_code = check_code(asset_code)
        for asset, units in self._holdings.items():
            if asset.code == asset_code:
                return units
        return 0

    def get_holding_weight(self, asset_code):
        asset_code = check_code(asset_code)
        for asset, units in self._holdings.items():
            if asset.code == asset_code:
                fx_pair = self._base_currency_code + asset.currency_code
                fx_rate = FxRate.get(fx_pair)
                asset_value = asset.local_value / fx_rate * units
                return asset_value / self._value
        return 0

    def __str__(self):
        holdings = self._holdings
        portfoliostr = "Portfolio('%s')" % self.base_currency_code
        assets_with_holdings = [
            asset for asset, units in holdings.items()
            if units != 0
        ]
        if len(assets_with_holdings) == 0:
            return portfoliostr

        return portfoliostr + ":\n" + "\n".join([
                str(asset) + ": " + "{0:,.0f}".format(holdings[asset])
                for asset in assets_with_holdings
        ])
