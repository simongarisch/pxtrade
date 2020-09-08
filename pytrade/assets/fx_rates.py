"""
Assets are setup such that they track their local value.
However, portfolios may consist of assets denominated in different currencies.
We'll need to value all assets in a chosen base currency.
To do this we need to keep track of FX rates.
"""
from weakref import WeakValueDictionary
from numbers import Real
from ..observable import Observable
from ..util import clean_string


def validate_pair(pair: str) -> str:
    if not isinstance(pair, str):
        raise TypeError("Expected string.")
    pair = clean_string(pair)
    if len(pair) != 6:
        raise ValueError("Expected a 6 character code.")
    return pair


def split_pair(pair):
    """ Return two individual components of the pair.
    >>> split_pair("AUDUSD")
    ('AUD', 'USD')
    """
    pair = validate_pair(pair)
    ccy1 = pair[:3]
    ccy2 = pair[3:]
    return ccy1, ccy2


def is_equivalent_pair(pair):
    """ Returns True where we expect the rate to be static.
        For example, AUDAUD = 1.0, USDUSD = 1.0
    >>> is_equivalent_pair("AUDAUD")
    True
    >>> is_equivalent_pair("AUDUSD")
    False
    """
    ccy1, ccy2 = split_pair(pair)
    if ccy1 == ccy2:
        return True
    return False


def get_inverse_pair(pair):
    """ Returns the inverse of some currency pair.
    >>> get_inverse_pair("AUDUSD")
    'USDAUD'
    """
    ccy1, ccy2 = split_pair(pair)
    return ccy2 + ccy1


class FxRate(Observable):
    """ Keep track of fx rates to value assets in different currencies.
        Notify all observers of a rate change.
    """
    _instances = WeakValueDictionary()

    def __init__(self, pair, rate):
        super().__init__()
        pair = validate_pair(pair)
        if pair in self._instances:
            raise ValueError("%s already created" % pair)
        inverse_pair = get_inverse_pair(pair)
        if inverse_pair in self._instances:
            raise ValueError("%s inverse pair already created" % inverse_pair)

        self._pair = pair
        self.rate = rate
        self._instances[pair] = self

    @property
    def rate(self):
        return self._rate

    @rate.setter
    def rate(self, rate):
        if rate is not None:
            if not isinstance(rate, Real):
                raise TypeError("Expecting numeric rate or None.")
            if rate <= 0:
                raise ValueError("FX rate must be > 0.")
        self._rate = rate
        self.notify_observers()

    @property
    def pair(self):
        """ This is read only. """
        return self._pair

    @classmethod
    def get(cls, pair):
        pair = validate_pair(pair)

        if is_equivalent_pair(pair):
            return 1.0

        fx = cls._instances.get(pair)
        if fx is not None:
            return fx.rate

        inverse_pair = get_inverse_pair(pair)
        fx = cls._instances.get(inverse_pair)
        if fx is not None:
            return 1 / fx.rate

        raise ValueError("%s rate not available" % pair)

    @classmethod
    def get_instance(cls, pair):
        pair = validate_pair(pair)
        instance = cls._instances.get(pair)
        if instance is None:
            raise ValueError("%s instance doesn't exist" % pair)
        return instance

    @classmethod
    def get_observable_instance(cls, pair):
        """ Return an instance representing either the
            currency pair (if available) or its inverse.
        """
        pair = validate_pair(pair)
        instance = cls._instances.get(pair)
        if instance is not None:
            return instance

        inverse_pair = get_inverse_pair(pair)
        instance = cls._instances.get(inverse_pair)
        if instance is not None:
            return instance

        raise ValueError("%s instance doesn't exist" % pair)
