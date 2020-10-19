"""
Here we test a very basic FX trading strategy for AUDUSD.
This is meant purely to test functionality.
Take a 100K USD portfolio.
Buy AUD if AUDUSD <= 0.6
Sell AUD if AUDUSD >= 0.7

PNL Using Adj. Close from yahoo finance:
On 18 Mar 2020 AUDUSD = 0.599219
On 07 Jun 2020 AUDUSD = 0.700241
If we bought and sold 100K AUD at these rates then:
* We'd pay USD $59,912 to enter the position
* Receive USD $70,024 on exit.
* For a trade pnl of 10,102 (=70,024-59,912)

Total portfolio value will be starting value + pnl.
"""
from datetime import date
from pxtrade import Trade
from pxtrade.assets import reset, Cash, FxRate, Portfolio
from pxtrade.backtest import Backtest
from pxtrade.strategy import Strategy
from pxtrade.events.yahoo import load_yahoo_prices
from pxtrade.compliance import Compliance, UnitLimit
from pxtrade.history import History


def test_audusd_strategy():
    reset()
    portfolio = Portfolio("USD")
    aud = Cash("AUD")
    usd = Cash("USD")
    audusd = FxRate("AUDUSD")
    amount = int(1e5)
    portfolio.transfer(usd, amount)

    portfolio.compliance = Compliance().add_rule(
        UnitLimit(aud, amount)
    )

    class AUDStrategy(Strategy):
        def generate_trades(self):
            audusd_rate = audusd.rate
            aud_holding = portfolio.get_holding_units("AUD")

            # establish a position when AUDUSD <= 0.6
            if audusd_rate <= 0.6:
                if int(aud_holding) == 0:
                    print("Buying at", audusd_rate)
                    return Trade(portfolio, aud, amount)

            # liquidate position (if any) when AUDUSD >= 0.7
            if audusd_rate >= 0.7:
                if int(aud_holding) > 0:
                    print("Selling at", audusd_rate)
                    return Trade(portfolio, aud, -aud_holding)

    history = History(portfolio)
    backtest = Backtest(AUDStrategy(), record_history=False)
    start_date = date(2020, 1, 1)
    end_date = date(2020, 9, 30)
    load_yahoo_prices(
        audusd, backtest,
        start_date=start_date,
        end_date=end_date,
    )

    backtest.run()
    print(portfolio)
    # from pandas_datareader import data as web
    # df = web.DataReader("AUDUSD=X", "yahoo", start_date, end_date)
    # df[df["Adj Close"] <= 0.6]
    # df[df["Adj Close"] >= 0.7]
    assert int(portfolio.value) == int(amount + 10102)

    df = history.get()
    assert len(df.index) == 0  # no history is recorded
