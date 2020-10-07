from copy import copy
from pytrade import trade
from pytrade import events
from .events_queue import EventsQueue
from .strategy import Strategy
from .history import History


class Backtest:
    def __init__(
        self,
        strategy=None,
        *,
        record_history=True,
    ):
        self._indicators = dict()
        self._events_queue = EventsQueue()
        self._datetime = None
        if strategy is not None:
            if not isinstance(strategy, Strategy):
                raise TypeError("Expecting Strategy instance.")
        self._strategy = strategy
        self._record_history = record_history

    def get_indicator(self, indicator_name):
        return self._indicators.get(indicator_name)

    def set_indicator(self, indicator_name, event_value):
        self._indicators[indicator_name] = event_value

    def load_event(self, event):
        self._events_queue.put(event)

    def _peek_next_event_datetime(self):
        queue = self._events_queue
        if queue.empty():
            return None
        datetime, _ = queue.queue[0]
        return datetime

    def _process_next_event(self) -> bool:
        queue = self._events_queue
        if queue.empty():
            return False
        self._datetime, event = queue.get()
        event.process()
        return True

    def _process_events_for_current_datetime(self):
        """ Process all events with the current time stamp. """
        peek_next_event_datetime = self._peek_next_event_datetime
        process_next_event = self._process_next_event
        current_datetime = self._datetime
        while current_datetime == peek_next_event_datetime():
            process_next_event()

    def _run_strategy(self):
        """ The strategy should return either a singular
            trade or a list of trades to execute.
        """
        strategy = self._strategy
        if strategy is None:
            return

        strategy_trades = strategy.generate_trades()
        if strategy_trades is None:
            return
        if isinstance(strategy_trades, trade.Trade):  # singular
            # print(self._datetime, strategy_trades)
            self.load_event(events.TradeEvent(
                self._datetime, strategy_trades
            ))
        else:
            for strategy_trade in strategy_trades:
                # print(self._datetime, strategy_trade)
                self.load_event(events.TradeEvent(
                    self._datetime, strategy_trade
                ))

    def run(self):
        """ Process all events in the queue with the same time stamp,
            then run your strategy.
            Continue this process until the queue is empty.
        """
        queue = self._events_queue
        process_next_event = self._process_next_event
        process_events_for_current_datetime = self._process_events_for_current_datetime  # noqa: E501
        take_history_snapshot = self._take_history_snapshot
        while True:
            process_next_event()  # primes self._datetime
            process_events_for_current_datetime()
            # once all events are processed for the current
            # time stamp we can run our strategy
            self._run_strategy()
            process_events_for_current_datetime()
            take_history_snapshot()
            if queue.empty():
                break

    def _take_history_snapshot(self):
        if not self._record_history:
            return
        for record in History.instances:
            record.take_snapshot(self._datetime)

    @property
    def num_events_loaded(self):
        return len(self._events_queue)

    @property
    def datetime(self):
        return copy(self._datetime)

    @property
    def indicators(self):
        return copy(self._indicators)
