""" Ensure codes are unique and associated with some security. """
from weakref import WeakValueDictionary
from ..util import clean_string


def check_code(code: str) -> str:
    """ Validates a proposed asset code.
    >>> check_code(" aapl ")
    'AAPL'
    """
    if not isinstance(code, str):
        raise TypeError("Expecting string.")
    return clean_string(code)


def check_currency_code(code: str) -> str:
    """ Validates a currency code such as 'AUD' or 'USD'.
    >>> check_currency_code(" GBP ")
    'GBP'
    """
    code = check_code(code)
    if len(code) != 3:
        raise ValueError("Expecting a 3 char code for currency.")
    return code


class Codes:
    def __init__(self):
        self._codes = WeakValueDictionary()

    def reset(self):
        self._codes = WeakValueDictionary()

    def register(self, code, associated_object) -> None:
        code = check_code(code)
        if self.code_in_use(code):
            if associated_object is self.get_object_for_code(code):
                return  # code is already registered with this object
            raise ValueError("Code is already in use.")
        self._codes[code] = associated_object

    def code_in_use(self, code) -> bool:
        code = check_code(code)
        if code in self._codes:
            return True
        return False

    def get_registered_codes(self):
        return sorted(list(self._codes))

    def get_object_for_code(self, code):
        code = check_code(code)
        return self._codes.get(code)

    def get_instances(self):
        return list(self._codes.values())
