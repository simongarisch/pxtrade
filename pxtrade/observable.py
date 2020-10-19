from weakref import WeakSet
from abc import ABC, abstractmethod


class Observable:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._observers = WeakSet()

    def add_observer(self, observer):
        self._observers.add(observer)

    def remove_observer(self, observer):
        self._observers.discard(observer)

    def notify_observers(self):
        for observer in self._observers:
            observer.observable_update(self)


class Observer(ABC):
    """ All observers must implement a observable_update method. """

    @abstractmethod
    def observable_update(self):
        raise NotImplementedError()  # pragma: no cover
