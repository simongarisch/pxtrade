from datetime import datetime
import pytest
import pandas as pd
from pytrading.assets import reset, Stock, Cash, Portfolio
from pytrading.history import History


class TestHistory(object):
    def setup_method(self, *args):
        reset()
        portfolio1 = self.portfolio1 = Portfolio("AUD", code="Portfolio")
        portfolio2 = self.portfolio2 = Portfolio("AUD", code="Benchmark")
        portfolios = self.portfolios = [portfolio1, portfolio2]
        cash = self.cash = Cash("AUD")
        stock = self.stock = Stock("ZZB", currency_code="AUD")
        stock.price = 0

        portfolio1.transfer(cash, 1000)
        portfolio2.transfer(cash, 2000)
        portfolio1.transfer(stock, 100)
        self.history = History(portfolios)

    def teardown_method(self):
        del self.portfolio1
        del self.portfolio2
        del self.portfolios
        del self.cash
        del self.stock
        del self.history

    def test_init(self):
        df = self.history.get()
        assert isinstance(df, pd.DataFrame)
        assert len(df.index) == 0

    def test_snapshots(self):
        date_time = datetime.now()
        index = pd.Timestamp(date_time)
        self.history.take_snapshot(date_time)
        df = self.history.get()
        assert isinstance(df, pd.DataFrame)
        assert len(df.index) == 1

        assert df.at[index, "Portfolio"] == 1000
        assert df.at[index, "Benchmark"] == 2000
        assert df.at[index, "ZZB"] == 0
        assert df.at[index, "AUD"] == 1
        assert df.at[index, "Portfolio_AUD"] == 1000
        assert df.at[index, "Benchmark_AUD"] == 2000
        assert df.at[index, "Portfolio_ZZB"] == 100
        assert df.at[index, "Benchmark_ZZB"] == 0

        self.stock.price = 20
        date_time = datetime.now()
        index = pd.Timestamp(date_time)
        self.history.take_snapshot(date_time)
        df = self.history.get()

        assert isinstance(df, pd.DataFrame)
        assert len(df.index) == 2
        assert df.at[index, "Portfolio"] == 3000
        assert df.at[index, "Benchmark"] == 2000
        assert df.at[index, "ZZB"] == 20
        assert df.at[index, "AUD"] == 1
        assert df.at[index, "Portfolio_AUD"] == 1000
        assert df.at[index, "Benchmark_AUD"] == 2000
        assert df.at[index, "Portfolio_ZZB"] == 100
        assert df.at[index, "Benchmark_ZZB"] == 0

    def test_types(self):
        # needs portfolio or list of portfolios
        with pytest.raises(TypeError):
            History(None)
        with pytest.raises(TypeError):
            History([None])

        # checks backtest instance
        with pytest.raises(TypeError):
            History(self.portfolios, backtest=123)

        # # only specific objects supported for history
        with pytest.raises(NotImplementedError):
            self.history._get_visitor(None)

        # snapshots require a datetime object
        with pytest.raises(TypeError):
            self.history.take_snapshot(None)
