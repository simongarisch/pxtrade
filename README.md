## pytrading
[![Build Status](https://travis-ci.org/simongarisch/pytrading.svg?branch=master)](https://travis-ci.org/simongarisch/pytrading)
[![Coverage Status](https://coveralls.io/repos/github/simongarisch/pytrading/badge.svg)](https://coveralls.io/github/simongarisch/pytrading?branch=master)

A multi currency, event driven backtester written in Python.


### Installation
```bash
pip install pytrading
```

### Examples
[Notebooks](https://github.com/simongarisch/pytrading/tree/master/notes) are available to cover the main concepts and examples.
-  [equities buy and hold](https://github.com/simongarisch/pytrading/blob/master/notes/06%20Example%20-%20Buy%20And%20Hold.ipynb)
-  [fx trading](https://github.com/simongarisch/pytrading/blob/master/notes/08%20Example%20-%20FX.ipynb)
-  [bitcoin](https://github.com/simongarisch/pytrading/blob/master/notes/09%20Example%20-%20Bitcoin.ipynb)
-  [Intraday trading](https://github.com/simongarisch/pytrading/blob/master/notes/11%20Example%20-%20FX%20Intraday%20with%20Benchmark.ipynb)

### Assets and Portfolios
Before we can run a backtest we need to define the assets and portfolios involved.
```python
from pytrading.assets import reset, Cash, Stock, FxRate, Portfolio


reset()
aud = Cash("AUD")
usd = Cash("USD")
audusd = FxRate("AUDUSD")
spy = Stock("SPY")
portfolio = Portfolio("USD", code="Portfolio")  # a portfolio denominated in USD
benchmark = Portfolio("USD", code="Benchmark")

print(portfolio)
```
    Portfolio('USD')
    


```python
portfolio.transfer(usd, 1e6)  # start both with 1M USD
benchmark.transfer(usd, 1e6)

print(portfolio)
```
    Portfolio('USD'):
    Cash('USD', 1.0, currency_code='USD'): 1,000,000
    

```python
portfolio.value
```
    1000000.0



### Imposing portfolio constraints through compliance
Ideally there will be risk limits in place when running a backtest. Some concrete compliance rules are provided, but you can also define your own by [inheriting from ComplianceRule](https://github.com/simongarisch/pytrading/blob/master/notes/02%20The%20Trade%20Lifecycle.ipynb).

```python
from pytrading.compliance import Compliance, UnitLimit


for port in [portfolio, benchmark]:
    port.compliance = Compliance().add_rule(
        UnitLimit(spy, 1000)
    )
```

### Defining a portfolio broker
Different portfolios / strategies are likely to vary materially in broker charges. All portfolios have a default broker that executes trades at the last price with no charge (or slippage). Brokers have separate execution and charges strategies. You can use the classes available or define custom strategies by inheriting from  [AbstractExecution](https://github.com/simongarisch/pytrading/blob/master/pytrading/broker/execution.py#L6) or [AbstractCharges](https://github.com/simongarisch/pytrading/blob/master/pytrading/broker/charges.py#L8). Note that backtesting supports multiple currencies. The portfolio could be denominated in USD, for example, but broker charges defined in AUD terms.


```python
from pytrading.broker import (
    Broker, 
    FillAtLastWithSlippage,
    FixedRatePlusPercentage,
)


portfolio.broker = Broker(
    execution_strategy=FillAtLastWithSlippage(0),  # no slippage, just fill at last
    charges_strategy=FixedRatePlusPercentage(20, 0, currency_code="AUD")  # fixed charge of AUD 20 per trade.
)
```

### Defining a trading strategy
All strategy classes must inherit from pytrading.Strategy and implement a generate_trades method. Note that the trades returned can either be None, a trade instance or list or trades.

```python
import pytrading as pt


class ExampleStrategy(pt.Strategy):
    def generate_trades(self):
        trades = list()

        # get the portfolio trades first
        if spy.price < 330:
            trades.append(pt.Trade(portfolio, spy, +100))

        trades.append(pt.Trade(benchmark, spy, +1000))

        return trades
```

### The backtest instance and trade history
A backtest takes a strategy instance as it's argument. Any instances of History then record state through time as events are processed.

```python
backtest = pt.Backtest(ExampleStrategy())

history = pt.History(
    portfolios=[portfolio, benchmark],
    backtest=backtest
)
```

### [Loading event data](https://github.com/simongarisch/pytrading/blob/master/notes/05%20Bulk%20Event%20Loads.ipynb)
Events can be loaded either from yahoo finance or from an existing data frame.

```python
from datetime import date
from pytrading.events.yahoo import load_yahoo_prices


start_date = date(2020, 6, 30)
end_date = date(2020, 9, 30)

load_yahoo_prices(
    [spy, audusd], backtest,
    start_date=start_date,
    end_date=end_date,
)
```

### Running the backtest and collecting history

```python
backtest.run()

df = history.get()
```

```python
df.columns
```
    Index(['AUD', 'AUDUSD', 'Benchmark', 'Benchmark_AUD', 'Benchmark_SPY',
           'Benchmark_USD', 'Portfolio', 'Portfolio_AUD', 'Portfolio_SPY',
           'Portfolio_USD', 'SPY', 'USD'],
          dtype='object')

```python
import cufflinks as cf


columns = ["Portfolio_SPY", "Benchmark_SPY", "SPY"]
df[columns].iplot(
    secondary_y="SPY",
    title="Portfolio Holdings of SPY",
)
```
![holdings](https://github.com/simongarisch/pytrading/blob/master/notes/portfolio_holdings_of_spy.png?raw=true)


```python
columns = ["Portfolio", "Benchmark"]
df[columns].iplot(
    title="Portfolio Value",
)
```
![holdings](https://github.com/simongarisch/pytrading/blob/master/notes/portfolio_value.png?raw=true)

***