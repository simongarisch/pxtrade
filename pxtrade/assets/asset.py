from typing import Union
from numbers import Real
from abc import ABC, abstractproperty
from .codes import check_code, check_currency_code, Codes
from .fx_rates import FxRate
from ..observable import Observable
from ..settings import get_default_currency_code


class Asset(ABC):
    """All asset objects must have a unique code.
    Each asset type must define it's own local_value property.
    """

    _codes = Codes()
    yahoo_ticker = None

    @classmethod
    def get_instances(cls):
        return cls._codes.get_instances()

    @classmethod
    def reset(cls):
        cls._codes.reset()
        FxRate.reset()

    @classmethod
    def get_asset_for_code(cls, code):
        return cls._codes.get_object_for_code(code)

    def __init__(
        self,
        code,
        price=None,
        *,
        currency_code=None,
        multiplier=1.0,
    ):
        super().__init__()
        if currency_code is None:
            currency_code = get_default_currency_code()
        code = check_code(code)
        currency_code = check_currency_code(currency_code)
        self._code = code
        self._currency_code = currency_code
        self._price = price
        self._multiplier = multiplier
        self._codes.register(code, self)

    # code, currency_code and multiplier are all read only after init
    @property
    def code(self):
        return self._code

    @property
    def currency_code(self):
        return self._currency_code

    @property
    def multiplier(self):
        """ multiplier is read only after init. """
        return self._multiplier

    @property
    def price(self):
        return self._price

    @abstractproperty
    def local_value(self):
        raise NotImplementedError()  # pragma: no cover

    def __str__(self):
        class_name = self.__class__.__name__
        return class_name + "('{}', {}, currency_code='{}')".format(
            self.code,
            self.price,
            self.currency_code,
        )


class StaticPriceAsset(Asset):
    """ Some assets will have a static price (e.g. cash). """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def local_value(self):
        return self._price * self._multiplier


class VariablePriceAsset(Asset, Observable):
    """ The price can be set and observed after init. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, price: Union[None, Real]):
        """ Call the revalue method when price changes. """
        if price is not None:
            if not isinstance(price, Real):
                raise TypeError("Expecting numeric price.")
        self._price = price
        self.notify_observers()

    @abstractproperty
    def local_value(self):
        raise NotImplementedError()  # pragma: no cover
