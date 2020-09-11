from datetime import datetime
from pytrade.assets import Stock
from pytrade.events import (
    AssetPriceEvent,
    EventsQueue
)


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

    print(first)
    assert first is event2
    assert second is event3
    assert third is event1
