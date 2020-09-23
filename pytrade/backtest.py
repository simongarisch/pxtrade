from .events_queue import EventsQueue


class Backtest:
    def __init__(self):
        self._indicators = dict()
        self._events_queue = EventsQueue()

    def get_indicator(self, indicator_name):
        return self._indicators.get(indicator_name)

    def set_indicator(self, indicator_name, event_value):
        self._indicators[indicator_name] = event_value

    def load_event(self, event):
        self._events_queue.put(event)

    def process_events(self):
        queue = self._events_queue
        while True:
            if queue.empty():
                return
            queue_item = queue.get()
            _, event = queue_item
            event.process()

    @property
    def num_events_loaded(self):
        return len(self._events_queue)
