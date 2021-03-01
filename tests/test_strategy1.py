"""
Here we test a basic buy and hold strategy for 100 shares of SPY.
The strategy is to:
-  Buy 100 shares of SPY @349.70 on Sep 1st
-  Hold until Oct 1st when the price is @335.61

PNL = (335.61 - 349.70) * 100 = -USD 1,409
"""
from datetime import date
import pandas as pd
from pxtrade import Trade
from pxtrade.assets import reset, Stock, Portfolio
from pxtrade.backtest import Backtest
from pxtrade.strategy import Strategy
from pxtrade.events.yahoo import load_yahoo_prices
from pxtrade.compliance import Compliance, UnitLimit
from pxtrade.history import History


def test_buy_and_hold():
    # create your stock and portfolio
    reset()
    spy = Stock("SPY", currency_code="USD")
    portfolio = Portfolio("USD")
    history = History(portfolio)

    # impose a compliance rule so we are unable to
    # hold more than 100 shares.
    portfolio.compliance = Compliance().add_rule(UnitLimit(spy, 100))

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
        spy,
        backtest,
        start_date=start_date,
        end_date=end_date,
    )

    # run the backtest and check pnl
    backtest.run()
    assert int(portfolio.value) == -1409
    df = history.get()

    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    # we hold a spy position of 100 shares from start to finish
    assert df.at[start_date, "Portfolio_SPY"] == 100
    assert df.at[end_date, "Portfolio_SPY"] == 100

    # a short position is held in USD (for the cost of stock purchase)
    assert int(df.at[start_date, "Portfolio_USD"]) == -34970

    # check on the start and ending prices for spy
    assert round(df.at[start_date, "SPY"], 2) == 349.70
    assert round(df.at[end_date, "SPY"], 2) == 335.61

    # and the portfolio value
    assert int(df.at[start_date, "Portfolio"]) == 0
    assert int(df.at[end_date, "Portfolio"]) == -1409
