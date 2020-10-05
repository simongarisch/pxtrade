"""
Here we test a basic buy and hold strategy for 100 shares of SPY.
The strategy is to:
-  Buy 100 shares of SPY @351.19 on Sep 1st
-  Hold until Oct 1st when the price is @337.04

PNL = (337.04 - 351.19) * 100 = -USD 1,415
"""
from datetime import date
from pytrade import Trade
from pytrade.assets import Asset, Stock, Portfolio
from pytrade.backtest import Backtest
from pytrade.strategy import Strategy
from pytrade.events.yahoo import load_yahoo_prices
from pytrade.compliance import Compliance, UnitLimit


def test_buy_and_hold():
    # create your stock and portfolio
    Asset.reset()
    spy = Stock("SPY", currency_code="USD")
    portfolio = Portfolio("USD")

    # impose a compliance rule so we are unable to
    # hold more than 100 shares.
    portfolio.compliance = Compliance().add_rule(
        UnitLimit(spy, 100)
    )

    # define a strategy to buy 100 shares at the outset.
    class BuyAndHold(Strategy):
        def generate_trades(self):
            return Trade(portfolio, spy, 100)

    # create your backtest instance
    backtest = Backtest(BuyAndHold())

    # load price events from yahoo
    start_date = date(2020, 9, 1)
    end_date = date(2020, 10, 1)
    load_yahoo_prices(
        spy, backtest,
        start_date=start_date,
        end_date=end_date,
    )

    # run the backtest and check pnl
    backtest.run()
    assert int(portfolio.value) == -1415
