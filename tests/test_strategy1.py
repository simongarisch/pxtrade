"""
Here we test a basic buy and hold strategy for 100 shares of SPY.
The strategy is to:
-  Buy 100 shares of SPY @351.19 on Sep 1st
-  Hold until Oct 1st when the price is @337.04

PNL = (337.04 - 351.19) * 100 = -USD 1,415
"""
from datetime import date
import pandas as pd
from pytrading import Trade
from pytrading.assets import reset, Stock, Portfolio
from pytrading.backtest import Backtest
from pytrading.strategy import Strategy
from pytrading.events.yahoo import load_yahoo_prices
from pytrading.compliance import Compliance, UnitLimit
from pytrading.history import History


def test_buy_and_hold():
    # create your stock and portfolio
    reset()
    spy = Stock("SPY", currency_code="USD")
    portfolio = Portfolio("USD")
    history = History(portfolio)

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
    df = history.get()

    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    # we hold a spy position of 100 shares from start to finish
    assert df.at[start_date, "Portfolio_SPY"] == 100
    assert df.at[end_date, "Portfolio_SPY"] == 100

    # a short position is held in USD (for the cost of stock purchase)
    assert int(df.at[start_date, "Portfolio_USD"]) == -35119

    # check on the start and ending prices for spy
    assert round(df.at[start_date, "SPY"], 2) == 351.19
    assert round(df.at[end_date, "SPY"], 2) == 337.04

    # and the portfolio value
    assert int(df.at[start_date, "Portfolio"]) == 0
    assert int(df.at[end_date, "Portfolio"]) == -1415
