""" Defines a proposed trade. """
from .assets import Asset


class ProposedTrade:
    def __init__(self, asset, units):
        if isinstance(asset, Asset):
            self._asset = asset
        else:
            if not isinstance(asset, str):
                raise TypeError("Expecting Asset instance or asset code.")
            asset = self._asset = Asset.get_asset_for_code(asset)
            if asset is None:
                raise ValueError("Asset code '%s' doesn't exist." % asset)
        if not isinstance(units, int):
            raise TypeError("Units for proposed trade must be an integer.")
        self._asset_code = asset.code
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

    def __str__(self):
        return (
            self.__class__.__name__
            + "('"
            + self._asset_code
            + "', "
            + str(self._units)
            + ")"
        )
