from .base import AbstractEvent


class IndicatorEvent(AbstractEvent):
    def __init__(
        self,
        indicator_name,
        datetime,
        event_value,
        *,
        backtest=None,
        validation_func=None,
    ):
        if not isinstance(indicator_name, str):
            raise TypeError("Expecting string.")
        if validation_func is not None:
            if not callable(validation_func):
                raise TypeError("Expecting a callable object.")

        self._indicator_name = indicator_name
        self._backtest = backtest
        self._validation_func = validation_func
        super().__init__(datetime, event_value)

    @property
    def indicator_name(self):
        return self._indicator_name

    def _validate(self, event_value):
        if self._validation_func is not None:
            self._validation_func(event_value)

    def _process(self):
        self._backtest.set_indicator(
            self._indicator_name, self.event_value
        )

    def __str__(self):
        return (
            self.__class__.__name__
            + "('"
            + str(self._indicator_name)
            + "', "
            + str(self._datetime)
            + ", "
            + str(self._event_value)
            + ")"
        )
