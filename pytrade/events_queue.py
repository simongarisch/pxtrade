from queue import PriorityQueue
from pytrade import AbstractEvent


class EventsQueue(PriorityQueue):
    def put(self, event):
        if not isinstance(event, AbstractEvent):
            raise TypeError("Only expecting Event objects in the queue.")
        super().put((event.datetime, event))

    def __len__(self):
        return len(self.queue)
