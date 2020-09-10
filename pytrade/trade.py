""" Defines a proposed trade. """
from .assets import Asset


class ProposedTrade:
    def __init__(self, asset_code, units):
        asset = self._asset = Asset.get_asset_for_code(asset_code)
        if asset is None:
            raise ValueError("Asset code '%s' doesn't exist." % asset_code)
        if not isinstance(units, int):
            raise TypeError("Units for proposed trade must be an integer.")
        self._asset_code = asset_code
        self._units = units

    @property
    def asset(self):
        return self._asset

    @property
    def asset_code(self):
        return self._asset_code

    @property
    def units(self):
        return self._units
