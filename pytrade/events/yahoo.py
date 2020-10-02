from typing import Union, List
from datetime import datetime, date
from pytrade.assets import Asset
from pytrade.util import clean_column_name, to_datetime
from pytrade.events import AssetPriceEvent
from pytrade.backtest import Backtest
from pandas_datareader import data as web


def load_yahoo_prices(
    assets: Union[Asset, List[Asset]],
    *args,
    **kwargs,
):
    if isinstance(assets, list):
        for asset in assets:
            _load(asset, *args, **kwargs)
    else:
        _load(assets, *args, **kwargs)


def _load(
    asset,
    backtest,
    *,
    ticker=None,
    start_date=date(1971, 1, 1),
    end_date=datetime.now().date(),
) -> None:
    if not isinstance(asset, Asset):
        raise TypeError("Expecting Asset instance.")
    if not isinstance(backtest, Backtest):
        raise TypeError("Expecting Backtest instance.")

    if ticker is None:
        ticker = asset.code
    else:
        if not isinstance(ticker, str):
            raise TypeError("Expecting string.")

    start_date = to_datetime(start_date)
    end_date = to_datetime(end_date)

    df = web.DataReader(ticker, "yahoo", start_date, end_date)
    df.columns = [clean_column_name(column) for column in df.columns]
    for event_datetime, row in df.iterrows():
        close = float(row["adj_close"])
        event = AssetPriceEvent(asset, event_datetime, close)
        if event_datetime < start_date or event_datetime > end_date:
            continue
        backtest.load_event(event)
