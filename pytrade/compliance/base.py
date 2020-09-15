"""
Before trades can be sent for execution they need to pass
any defined compliance rules. These rules may include position
limits, restricted securities, ...
Here compliance rules have been arranged using a composite pattern
to check portfolio positions should the trade be fully executed.
"""
from abc import ABC, abstractmethod
from ..assets import Portfolio


class ComplianceRule(ABC):
    @abstractmethod
    def passes(self, portfolio) -> bool:
        raise NotImplementedError  # pragma: no cover


class Compliance(ComplianceRule):
    """ All compliance rule components have to pass for
        compliance as a whole to pass.
    """
    def __init__(self):
        self._rules = set()

    def add_rule(self, rule):
        if not isinstance(rule, ComplianceRule):
            raise TypeError("Expecting Compliance Rule instance.")
        self._rules.add(rule)

    def remove_rule(self, rule):
        self._rules.discard(rule)

    def passes(self, portfolio):
        if not isinstance(portfolio, Portfolio):
            raise TypeError("Expecting Portfolio instance.")

        for rule in self._rules:
            if not rule.passes(portfolio):
                return False
        return True
