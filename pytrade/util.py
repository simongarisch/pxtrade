from numbers import Real


def clean_string(s: str) -> str:
    """ Cleans and returns an input string
    >>> clean_string(" xYz ")
    'XYZ'
    """
    return str(s).strip().upper()


def check_positive_numeric(x):
    """ Check that some value is both numeric and >= 0
        before returning it.
    """
    if not isinstance(x, Real):
        raise TypeError("Expecting numeric value.")
    if x < 0:
        raise ValueError("Value must be >= 0")
    return x
