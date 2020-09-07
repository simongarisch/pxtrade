from weakref import WeakSet


class Observable:
    def __init__(self):
        self._observers = WeakSet()

    def add_observer(self, observer):
        self._observers.add(observer)

    def remove_observer(self, observer):
        self._observers.discard(observer)

    def notify_observers(self):
        for observer in self._observers:
            observer.observable_update(self)
