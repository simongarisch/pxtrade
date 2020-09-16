from numbers import Real
from .base import ComplianceRule
from ..assets import Asset


class UnitLimit(ComplianceRule):
    def __init__(self, asset, unit_limit):
        super().__init__()
        if not isinstance(asset, Asset):
            raise TypeError("Expecting Asset instance.")
        if not isinstance(unit_limit, int):
            raise TypeError("Expecting integer.")
        self._asset = asset
        self._unit_limit = abs(unit_limit)

    def passes(self, portfolio) -> bool:
        position = portfolio.get_holding_units(self._asset.code)
        if abs(position) > self._unit_limit:
            return False
        return True

    def __str__(self):
        return (
            self.__class__.__name__
            + "('%s', %s)" % (
                self._asset.code, "{:,}".format(self._unit_limit)
            )
        )


class WeightLimit(ComplianceRule):
    def __init__(self, asset, weight_limit):
        super().__init__()
        if not isinstance(asset, Asset):
            raise TypeError("Expecting Asset instance.")
        if not isinstance(weight_limit, Real):
            raise TypeError("Expecting numeric value.")
        self._asset = asset
        self._weight_limit = abs(weight_limit)

    def passes(self, portfolio) -> bool:
        weight = portfolio.get_holding_weight(self._asset.code)
        if abs(weight) > self._weight_limit:
            return False
        return True

    def __str__(self):
        return (
            self.__class__.__name__
            + "('%s', %0.2f)" % (self._asset.code, self._weight_limit)
        )
