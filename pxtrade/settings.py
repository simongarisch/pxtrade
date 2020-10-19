import os
from configparser import ConfigParser
from .assets.codes import check_currency_code


config = ConfigParser()
dire_path = os.path.dirname(os.path.abspath(__file__))
config.read(os.path.join(dire_path, "settings.ini"))


def set_default_currency_code(code: str = "USD"):
    code = check_currency_code(code)
    config["currency"]["default"] = code


def get_default_currency_code():
    return config["currency"]["default"]
