from .asset import Asset, StaticPriceAsset
from .codes import check_currency_code


class Cash(StaticPriceAsset):
    def __init__(self, code):
        code = check_currency_code(code)
        super().__init__(
            code,
            price=1.0,
            currency_code=code,
            multiplier=1.0,
        )


def get_cash(currency_code):
    currency_code = check_currency_code(currency_code)
    cash = Asset.get_asset_for_code(currency_code)
    if cash is not None:
        if not isinstance(cash, Cash):
            raise TypeError(  # code already taken by cash asset
                "Currency code '%s' is reserved for cash." % currency_code
            )
    else:
        cash = Cash(currency_code)
    return cash
