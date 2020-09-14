from .events_queue import EventsQueue


class Backtest:
    def __init__(self):
        self._indicators = dict()
        self._events_queue = EventsQueue()

    def get_indicator(self, indicator_name):
        return self._indicators.get(indicator_name)

    def set_indicator(self, indicator_name, event_value):
        self._indicators[indicator_name] = event_value

    def _process_event(self, event):
        event.process()

    def load_event(self, event):
        self._events_queue.put(event)
