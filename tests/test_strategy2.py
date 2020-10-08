"""
Here we test a basic strategy that includes an indicator and FX rate movements.

We'll start with an ($100K) AUD denominated portfolio and buy 100 shares of SPY
only if the VIX < 26.

Also, buying in SPY will make us short USD.
Generate funding trades, to be executed the day after we buy SPY, so that
we aren't short USD.

For the sake of testing we'll focus on the dates 1st Sep -> 1st Oct.
Points to note:
-  We'll buy 100 shares of SPY @337.11 on Sep 14th VIX=25.85
-  Hold until Oct 1st when SPY=337.04, AUDUSD=0.7167
-  Because our portfolio is denominated in AUD we need to calculate AUD prices.
-  So buying SPY at 337.11 (Sep 14th price) / 0.729682 (fx 15th) = AUD 462
-  And holding to a value of 337.04 / 0.716651 = AUD 470.30
-  PNL will be $8.30 (= 470.30 - 462.00) for each of 100 shares purchased.
"""
from datetime import date
import pandas as pd
from pytrade import Trade
from pytrade.assets import reset, Stock, Cash, FxRate, Portfolio
from pytrade.backtest import Backtest
from pytrade.strategy import Strategy
from pytrade.events.yahoo import load_yahoo_prices
from pytrade.compliance import Compliance, UnitLimit
from pytrade.history import History


def test_buy_spy_with_indicator():
    # create your stock and portfolio
    reset()
    spy = Stock("SPY", currency_code="USD")
    aud = Cash("AUD")
    usd = Cash("USD")
    audusd = FxRate("AUDUSD")
    portfolio = Portfolio("AUD")
    starting_value = 1e5  # start with $100K AUD
    portfolio.transfer(aud, starting_value)

    # impose a compliance rule so we are unable to
    # hold more than 100 shares.
    portfolio.compliance = Compliance().add_rule(
        UnitLimit(spy, 100)
    )

    # define a strategy to buy 100 shares of SPY
    # if we are short USD then also fund this shortfall with AUD
    class BuySpyWithIndicator(Strategy):
        def show(self, trades):
            if len(trades) == 0:
                return
            print(backtest.datetime)
            print("^VIX: ", backtest.get_indicator("^VIX"))
            print("AUDUSD: ", audusd.rate)
            print("SPY: ", spy.price)
            for trade in trades:
                print(trade)
            print("-------")

        def generate_trades(self):
            trades = list()
            usd_holding = portfolio.get_holding_units("USD")
            if usd_holding < 0:
                trades.append(Trade(portfolio, usd, int(-usd_holding)+1))

            if backtest.get_indicator("^VIX") >= 26:
                # don't buy any spy, just fund usd (if required)
                self.show(trades)
                return trades

            trades.append(Trade(portfolio, spy, 100))
            self.show(trades)
            return trades

    # create your backtest instance
    backtest = Backtest(BuySpyWithIndicator())
    history = History(
        portfolios=portfolio,
        backtest=backtest,
    )

    # load price events from yahoo for spy, audusd, vix
    start_date = date(2020, 9, 1)
    end_date = date(2020, 10, 1)
    load_yahoo_prices(
        [spy, audusd, "^VIX"],
        backtest,
        start_date=start_date,
        end_date=end_date,
    )

    # run the backtest and check pnl
    backtest.run()
    df = history.get()
    # print(portfolio)
    # print(audusd.rate)
    print(backtest.datetime)
    print(df)
    assert int(portfolio.value) == int(starting_value + 830)

    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    assert int(df.at[start_date, "Portfolio"]) == int(starting_value)
    assert int(df.at[end_date, "Portfolio"]) == int(starting_value + 830)
    assert round(df.at[end_date, "AUDUSD"], 5) == 0.71665
    assert round(df.at[pd.Timestamp(date(2020, 9, 14)), "^VIX"], 2) == 25.85
