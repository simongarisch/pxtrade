import pytest
from pytrade.assets import Stock
from pytrade import trade


def test_proposed_trade_init():
    zzb = Stock("ZZB AU", 2.50, currency_code="AUD")
    assert isinstance(zzb, Stock)
    assert zzb.code == "ZZB AU"
    proposed_trade = trade.ProposedTrade("ZZB AU", 100)
    assert proposed_trade.asset_code == "ZZB AU"
    assert proposed_trade.units == 100


def test_proposed_trade_init_with_asset():
    zzb = Stock("ZZB AU", 2.50, currency_code="AUD")
    proposed_trade = trade.ProposedTrade(zzb, 100)
    assert proposed_trade.asset is zzb
    assert proposed_trade.asset_code == "ZZB AU"
    assert proposed_trade.units == 100
    with pytest.raises(TypeError):
        trade.ProposedTrade(123, 100)


def test_proposed_trade_immutable():
    zzz = Stock("ZZZ AU", 2.50, currency_code="AUD")
    assert zzz.code == "ZZZ AU"
    proposed_trade = trade.ProposedTrade("ZZZ AU", 200)
    assert proposed_trade.asset_code == "ZZZ AU"
    assert proposed_trade.units == 200
    assert proposed_trade.asset is zzz
    with pytest.raises(AttributeError):
        proposed_trade.asset_code = "YYY AU"
    with pytest.raises(AttributeError):
        proposed_trade.units = 500


def test_proposed_trade_no_asset():
    with pytest.raises(ValueError):
        trade.ProposedTrade(
            "NO_ASSET_WITH_THIS_CODE", 200
        )


def test_units_must_be_int():
    zzb = Stock("ZZB AU", 2.50, currency_code="AUD")
    proposed_trade = trade.ProposedTrade("ZZB AU", 100)
    assert proposed_trade.asset is zzb
    assert proposed_trade.units == 100
    with pytest.raises(TypeError):
        proposed_trade = trade.ProposedTrade("ZZB AU", "100")
