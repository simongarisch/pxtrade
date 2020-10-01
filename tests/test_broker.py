import pytest
from pytrade import Trade, Broker
from pytrade.assets import (
    Asset,
    Stock,
    Cash,
    FxRate,
    Portfolio,
)
from pytrade.broker import (
    AbstractExecution,
    AbstractCharges,
    FillAtLastWithSlippage,
    FixedRatePlusPercentage,
)


class TestBroker(object):
    def setup_method(self, *args):
        portfolio = self.portfolio = Portfolio("AUD")
        aud = Asset.get_asset_for_code("AUD")
        if aud is not None:
            self.aud = aud
        else:
            aud = self.aud = Cash("AUD")
        portfolio.transfer(aud, 1000)
        stock = self.stock = Stock("TEST AU", 2.50, currency_code="AUD")
        self.buy_trade = Trade(portfolio, stock, 100)
        self.sell_trade = Trade(portfolio, stock, -100)

    def teardown_method(self):
        del self.portfolio
        del self.aud
        del self.stock
        del self.buy_trade
        del self.sell_trade

    def test_default_broker(self):
        """ Fill at last with no charges. """
        portfolio = self.portfolio
        assert portfolio.value == 1000
        broker = Broker()

        broker.execute(self.buy_trade)
        assert portfolio.get_holding_units("TEST AU") == 100
        assert portfolio.get_holding_units("AUD") == 750

        broker.execute(self.sell_trade)
        assert portfolio.value == 1000
        assert portfolio.get_holding_units("TEST AU") == 0
        assert portfolio.get_holding_units("AUD") == 1000

        with pytest.raises(TypeError):
            broker.execute("trade")

    def test_broker_with_slippage(self):
        """
        Trade will be executed at last with slippage.
        Slippage is 1% of traded value ($250 * 0.01 = $2.50)
        """
        portfolio = self.portfolio
        broker = Broker(execution_strategy=FillAtLastWithSlippage(0.01))
        assert portfolio.value == 1000

        broker.execute(self.buy_trade)
        assert portfolio.value == 1000 - 2.50
        assert portfolio.get_holding_units("TEST AU") == 100
        assert portfolio.get_holding_units("AUD") == 750 - 2.50

        broker.execute(self.sell_trade)
        assert portfolio.value == 1000 - 5.0
        assert portfolio.get_holding_units("TEST AU") == 0
        assert portfolio.get_holding_units("AUD") == 1000 - 5.0

    def test_broker_charges_aud(self):
        """
        Apply a fixed rate + % charges from broker.
        Fixed charge is $20 AUD and percentage in this case is 1% = 2.50.
        """
        portfolio = self.portfolio
        charges_strategy = FixedRatePlusPercentage(
            20, 0.01, currency_code="AUD"
        )
        broker = Broker(charges_strategy=charges_strategy)
        assert portfolio.value == 1000

        broker.execute(self.buy_trade)
        assert portfolio.value == 1000 - 20 - 2.50
        assert portfolio.get_holding_units("TEST AU") == 100
        assert portfolio.get_holding_units("AUD") == 750 - 20 - 2.50

        broker.execute(self.sell_trade)
        assert portfolio.value == 1000 - 40 - 5.0
        assert portfolio.get_holding_units("TEST AU") == 0
        assert portfolio.get_holding_units("AUD") == 1000 - 40 - 5.0

    def test_broker_charges_usd(self):
        portfolio = self.portfolio
        audusd = FxRate("AUDUSD", 0.5)
        assert audusd.rate == 0.5
        assert FxRate.get("AUDUSD") == 0.5
        assert FxRate.get("USDAUD") == 2.0

        charges_strategy = FixedRatePlusPercentage(
            20, 0.01, currency_code="USD"
        )
        broker = Broker(charges_strategy=charges_strategy)
        assert portfolio.value == 1000
        get_holding_units = portfolio.get_holding_units

        aud_fixed_charge = 20 / 0.5  # 20 USD converted to AUD
        aud_perc_charge = 2.50
        usd_perc_charge = 2.50 * 0.5
        total_aud_charge = aud_fixed_charge + aud_perc_charge

        broker.execute(self.buy_trade)
        assert portfolio.value == 1000 - total_aud_charge
        assert get_holding_units("TEST AU") == 100
        assert get_holding_units("AUD") == 750
        assert get_holding_units("USD") == -(20 + usd_perc_charge)

        broker.execute(self.sell_trade)
        assert portfolio.value == 1000 - (total_aud_charge) * 2
        assert get_holding_units("TEST AU") == 0
        assert get_holding_units("AUD") == 1000
        assert get_holding_units("USD") == -(20 + usd_perc_charge) * 2

    def test_charge_types(self):
        with pytest.raises(TypeError):
            FixedRatePlusPercentage("10", 0.01)
        with pytest.raises(TypeError):
            FixedRatePlusPercentage(10, "0.01")
        with pytest.raises(ValueError):
            FixedRatePlusPercentage(-10, 0.01)
        with pytest.raises(ValueError):
            FixedRatePlusPercentage(10, -0.01)
        charges_strategy = FixedRatePlusPercentage(10, 0.01)
        assert isinstance(charges_strategy, AbstractCharges)

    def test_execution_types(self):
        execution_strategy = FillAtLastWithSlippage(0.01)
        assert isinstance(execution_strategy, AbstractExecution)
        with pytest.raises(TypeError):
            FillAtLastWithSlippage("0.01")
        with pytest.raises(ValueError):
            FillAtLastWithSlippage(-0.01)
