""" A strategy pattern for charges applied in trade execution. """
from abc import ABC, abstractmethod
from numbers import Real
from ..settings import get_default_currency_code
from .. import assets


class AbstractCharges(ABC):
    @abstractmethod
    def charge(self, trade):
        raise NotImplementedError()  # pragma: no cover


class NoCharges(AbstractCharges):
    def charge(self, trade):
        """ No charges will be applied for the trade. """
        pass


class FixedRatePlusPercentage(AbstractCharges):
    def __init__(self, fixed_amount, percentage, *, currency_code=None):
        super().__init__()
        if not isinstance(fixed_amount, Real):
            raise TypeError("Expecting numeric for fixed_amount.")
        if not isinstance(percentage, Real):
            raise TypeError("Expecting numeric for percentage.")
        if fixed_amount < 0:
            raise ValueError("Charge amount should be >= 0.")
        if percentage < 0:
            raise ValueError("Percentage charge should be >= 0.")
        self._fixed_amount = fixed_amount
        self._percentage = percentage
        if currency_code is None:
            currency_code = get_default_currency_code()
        self._currency_code = assets.check_currency_code(currency_code)

    def charge(self, trade):
        asset = trade.asset
        units = trade.units
        charge_currency_code = self._currency_code
        asset_currency_code = asset.currency_code
        portfolio = trade.portfolio

        # calculate total charges
        charge_cash = assets.get_cash(charge_currency_code)
        local_value_traded = abs(asset.local_value * units)
        percentage_charge_local = abs(self._percentage * local_value_traded)
        fx_rate = assets.FxRate.get(asset_currency_code + charge_currency_code)
        percentage_charge = percentage_charge_local * fx_rate

        total_charge = self._fixed_amount + percentage_charge
        portfolio.transfer(charge_cash, -total_charge)
        return charge_cash, -total_charge
