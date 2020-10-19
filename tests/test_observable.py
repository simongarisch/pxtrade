from pxtrade.observable import Observable


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


def test_observer_add_discard():
    observable = Something()
    observer1 = Observer()
    observer2 = Observer()

    for observer in [observer1, observer2]:
        observable.add_observer(observer)
        assert observer.observes is None

    observable.status = "round1"
    observable.notify_observers()
    for observer in [observer1, observer2]:
        assert observer.observes == "round1"

    observable.remove_observer(observer2)
    observable.status = "round2"
    observable.notify_observers()
    assert observer1.observes == "round2"
    assert observer2.observes == "round1"
