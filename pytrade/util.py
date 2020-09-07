
def clean_string(s: str) -> str:
    """ Cleans and returns an input string
    >>> clean_string(" xYz ")
    'XYZ'
    """
    return str(s).strip().upper()
