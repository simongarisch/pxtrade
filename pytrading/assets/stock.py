from .asset import VariablePriceAsset


class Stock(VariablePriceAsset):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def local_value(self):
        if self._price is None:
            return None
        return self._price * self._multiplier
