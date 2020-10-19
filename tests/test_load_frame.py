from datetime import date
import pytest
import pandas as pd
from pxtrade.assets import reset, Stock, FxRate, Portfolio
from pxtrade.backtest import Backtest
from pxtrade.strategy import Strategy
from pxtrade.history import History
from pxtrade.events import (
    AssetPriceEvent,
    FxRateEvent,
    IndicatorEvent,
    load_frame_events,
)


class DoNothingStrategy(Strategy):
    def generate_trades(self):
        return None  # don't trade


class TestLoadFrame(object):
    def setup_method(self, *args):
        reset()
        self.stock = Stock("SPY")
        self.fx_rate = FxRate("XXXYYY")
        portfolio = self.portfolio = Portfolio("USD")
        backtest = self.backtest = Backtest(DoNothingStrategy())
        self.history = History(
            portfolios=portfolio,
            backtest=backtest,
        )

        dates = [date(2020, 9, 1), date(2020, 9, 2)]
        values = [1.1, 1.2]
        df = pd.DataFrame(values, dates, columns=["column_name"])
        df.index = pd.to_datetime(df.index)
        self.df = df

    def teardown_method(self, *args):
        del self.stock
        del self.fx_rate
        del self.portfolio
        del self.backtest
        del self.history

    def test_load_frame_price_events(self):
        events_loaded = load_frame_events(
            self.stock,
            self.df.copy(),
            "column_name",
            backtest=self.backtest,
            event_class=AssetPriceEvent,
        )
        assert events_loaded == 2

        self.backtest.run()
        df = self.history.get()
        assert len(df.index) == 2
        prices = df["SPY"].values
        assert prices[0] == 1.1
        assert prices[1] == 1.2
        assert self.stock.price == 1.2

    def test_load_frame_fx_events(self):
        load_frame_events(
            self.fx_rate,
            self.df.copy(),
            "column_name",
            backtest=self.backtest,
            event_class=FxRateEvent,
        )

        self.backtest.run()
        df = self.history.get()
        assert len(df.index) == 2
        prices = df["XXXYYY"].values
        assert prices[0] == 1.1
        assert prices[1] == 1.2
        assert self.fx_rate.rate == 1.2

    def test_load_frame_indicator_events(self):
        load_frame_events(
            "IndicatorCode",
            self.df.copy(),
            "column_name",
            backtest=self.backtest,
            event_class=IndicatorEvent,
        )

        self.backtest.run()
        df = self.history.get()
        assert len(df.index) == 2
        prices = df["IndicatorCode"].values
        assert prices[0] == 1.1
        assert prices[1] == 1.2
        assert self.backtest.get_indicator("IndicatorCode") == 1.2

    def test_types(self):
        # no events are loaded from an empty data frame
        events_loaded = load_frame_events(
            "IndicatorCode",
            pd.DataFrame(),
            "column_name",
            backtest=self.backtest,
            event_class=IndicatorEvent,
        )
        assert events_loaded == 0

        with pytest.raises(TypeError):
            # needs a pd.DataFrame instance
            events_loaded = load_frame_events(
                "XXX",
                "NoDataFrame",
                "column_name",
                backtest=self.backtest,
                event_class=IndicatorEvent,
            )

        with pytest.raises(TypeError):
            # with a column as string
            events_loaded = load_frame_events(
                "XXX",
                pd.DataFrame(),
                None,
                backtest=self.backtest,
                event_class=IndicatorEvent,
            )

        with pytest.raises(TypeError):
            # needs a backtest instance
            events_loaded = load_frame_events(
                "XXX",
                pd.DataFrame(),
                "column_name",
                backtest="NoBacktest",
                event_class=IndicatorEvent,
            )

        with pytest.raises(TypeError):
            # expecting a class
            events_loaded = load_frame_events(
                "XXX",
                pd.DataFrame(),
                "column_name",
                backtest=self.backtest,
                event_class="NotAClass",
            )

        with pytest.raises(TypeError):
            # expecting an event class
            class MyClass:
                pass

            events_loaded = load_frame_events(
                "XXX",
                pd.DataFrame(),
                "column_name",
                backtest=self.backtest,
                event_class=MyClass,
            )

    def test_df_datetime_index(self):
        df = self.df.copy()
        df.index = [1, 2]
        with pytest.raises(TypeError):
            load_frame_events(
                "IndicatorCode",
                df,
                "column_name",
                backtest=self.backtest,
                event_class=IndicatorEvent,
            )
