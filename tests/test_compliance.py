import pytest
from pytrading.assets import reset, Stock, Portfolio
from pytrading.compliance import (
    Compliance,
    UnitLimit,
    WeightLimit,
)


class TestCompliance(object):
    def setup_method(self, *args):
        reset()
        stock1 = self.stock1 = Stock("BBB US", 2.00, currency_code="USD")
        stock2 = self.stock2 = Stock("CCC US", 2.00, currency_code="USD")
        portfolio = self.portfolio = Portfolio("USD")
        portfolio.transfer(stock1, 200)
        portfolio.transfer(stock2, 200)
        self.compliance = Compliance()

    def test_compliance(self):
        with pytest.raises(TypeError):
            # Requires a ComplianceRule instance.
            self.compliance.add_rule("ZZZ")
        with pytest.raises(TypeError):
            # Requires a Portfolio instance.
            self.compliance.passes("ZZZ")

    def teardown_method(self, *args):
        del self.stock1
        del self.stock2
        del self.portfolio
        del self.compliance

    def test_unit_limit(self):
        with pytest.raises(TypeError):
            # Requires an Asset instance
            UnitLimit("ABC US", 100)
        with pytest.raises(TypeError):
            # Limit must be an integer.
            UnitLimit(self.stock1, "100")

        rule = UnitLimit(self.stock1, 200)
        compliance = self.compliance
        portfolio = self.portfolio
        compliance.add_rule(rule)
        assert compliance.passes(portfolio)

        portfolio.transfer(self.stock1, 1)
        assert not compliance.passes(portfolio)
        compliance.remove_rule(rule)
        assert compliance.passes(portfolio)

    def test_unit_limit_str(self):
        rule = UnitLimit(self.stock1, 200)
        assert str(rule) == "UnitLimit('BBB US', 200)"
        rule = UnitLimit(self.stock1, 1000)
        assert str(rule) == "UnitLimit('BBB US', 1,000)"

    def test_weight_limit(self):
        with pytest.raises(TypeError):
            # Requires an Asset instance
            WeightLimit("ABC US", 0.5)
        with pytest.raises(TypeError):
            # Limit must be an integer.
            WeightLimit(self.stock2, "0.5")

        rule = WeightLimit(self.stock2, 0.50)
        compliance = self.compliance
        portfolio = self.portfolio
        compliance.add_rule(rule)
        assert compliance.passes(portfolio)

        portfolio.transfer(self.stock2, 1)
        assert not compliance.passes(portfolio)
        compliance.remove_rule(rule)
        assert compliance.passes(portfolio)

    def test_weight_limit_str(self):
        rule = WeightLimit(self.stock2, 0.50)
        assert str(rule) == "WeightLimit('CCC US', 0.50)"
