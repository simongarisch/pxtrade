import os
from configparser import ConfigParser
from .assets.codes import check_currency_code


config = ConfigParser()
config.read(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.ini")
)


def set_default_currency_code(code: str = "USD"):
    code = check_currency_code(code)
    config["currency"]["default"] = code


def get_default_currency_code():
    return config["currency"]["default"]
