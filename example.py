from datetime import datetime
from pytrade import Trade
from pytrade.assets import Stock, Portfolio
from pytrade.backtest import Backtest
from pytrade.strategy import Strategy
from pytrade.events import AssetPriceEvent
from pytrade.compliance import Compliance, UnitLimit


portfolio = Portfolio("AUD")
stock = Stock("ZZB AU", 2.50, currency_code="AUD")
events = [
    AssetPriceEvent(stock, datetime(2020, 9, 1), 2.50),
    AssetPriceEvent(stock, datetime(2020, 9, 2), 2.60),
    AssetPriceEvent(stock, datetime(2020, 9, 3), 2.70),
]

compliance = Compliance()
compliance.add_rule(UnitLimit(stock, 5))
portfolio.compliance = compliance


class BasicStrategy(Strategy):
    """ Continue to buy one share of 'ZZB AU'. """
    def generate_trades(self):
        return Trade(portfolio, stock, 1)


backtest = Backtest(BasicStrategy())
[backtest.load_event(event) for event in events]
backtest.run()

print(portfolio.get_holding_units("ZZB AU"))
print(portfolio.get_holding_units("AUD"))
