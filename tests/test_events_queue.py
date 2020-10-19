from datetime import datetime
import pytest
from pxtrade import EventsQueue
from pxtrade.assets import Stock
from pxtrade.events import AssetPriceEvent


def test_queue_order():
    """ Items should be retrieved from the queue from oldest to newest """
    queue = EventsQueue()
    stock = Stock("ZZZ")
    event1 = AssetPriceEvent(stock, datetime(2020, 9, 3), 2.65)
    event2 = AssetPriceEvent(stock, datetime(2020, 9, 1), 2.55)
    event3 = AssetPriceEvent(stock, datetime(2020, 9, 2), 2.60)
    [queue.put(event) for event in [event1, event2, event3]]
    assert len(queue) == 3

    _, first = queue.get()
    _, second = queue.get()
    _, third = queue.get()
    assert len(queue) == 0

    assert first is event2
    assert second is event3
    assert third is event1


def test_queue_type():
    queue = EventsQueue()
    stock = Stock("ZZZ")
    event = AssetPriceEvent(stock, datetime(2020, 9, 3), 2.65)
    queue.put(event)
    assert len(queue) == 1
    with pytest.raises(TypeError):
        queue.put(123)
    assert len(queue) == 1
