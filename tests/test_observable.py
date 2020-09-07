from pytrade.observable import Observable


class Something(Observable):
    status = None


class Observer:
    observes = None

    def observable_update(self, observable):
        self.observes = observable.status


def test_observable():
    observable = Something()
    observer = Observer()
    observable.add_observer(observer)

    assert observer.observes is None
    observable.status = "ready"
    observable.notify_observers()
    assert observer.observes == "ready"
