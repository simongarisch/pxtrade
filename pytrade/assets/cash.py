from .asset import StaticPriceAsset
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
