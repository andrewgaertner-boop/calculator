"""Calculator core with Observer pattern, undo/redo, and history persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from app.calculation import Calculation
from app.calculator_config import CalculatorConfig, load_config
from app.calculator_memento import CalculatorMemento, Caretaker
from app.exceptions import HistoryError
from app.history import HistoryManager
from app.logger import get_logger, setup_logging
from app.operations import OperationFactory

logger = get_logger("core")


class Observer(ABC):
    """Observer interface notified when a new calculation occurs."""

    @abstractmethod
    def update(self, calculation: Calculation, calculator: "Calculator") -> None:
        """React to a newly performed calculation."""


class LoggingObserver(Observer):
    """Logs each calculation's operation, operands, and result."""

    def update(self, calculation: Calculation, calculator: "Calculator") -> None:
        logger.info(
            "Calculation: %s(%s, %s) = %s",
            calculation.operation,
            calculation.operand1,
            calculation.operand2,
            calculation.result,
        )


class AutoSaveObserver(Observer):
    """Automatically saves history to CSV when auto-save is enabled."""

    def update(self, calculation: Calculation, calculator: "Calculator") -> None:
        if calculator.config.auto_save:
            try:
                calculator.history.save()
                logger.debug("Auto-saved history after %s", calculation)
            except HistoryError as exc:
                logger.error("Auto-save failed: %s", exc)


class Calculator:
    """
    Enhanced calculator coordinating operations, history, mementos, and observers.
    """

    def __init__(self, config: Optional[CalculatorConfig] = None) -> None:
        self.config = config or load_config()
        setup_logging(self.config.log_file, encoding=self.config.default_encoding)

        self.history = HistoryManager(
            history_file=self.config.history_file,
            max_size=self.config.max_history_size,
            encoding=self.config.default_encoding,
        )
        self._caretaker = Caretaker()
        self._observers: List[Observer] = []

        self.add_observer(LoggingObserver())
        self.add_observer(AutoSaveObserver())
        logger.info("Calculator initialized")

    # Observer management

    def add_observer(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify(self, calculation: Calculation) -> None:
        for observer in list(self._observers):
            observer.update(calculation, self)

    # Calculation logic

    def calculate(self, operation_name: str, a: float, b: float) -> Calculation:
        """
        Perform an operation, update history with memento support, and notify observers.
        """
        # Save previous history snapshot for undo
        previous = CalculatorMemento.from_history(self.history.entries)
        calculation = Calculation.create(
            operation_name=operation_name,
            operand1=a,
            operand2=b,
            precision=self.config.precision,
        )
        self._caretaker.save(previous)
        self.history.add(calculation)
        self._notify(calculation)
        return calculation

    # History persistence

    def get_history(self) -> List[Calculation]:
        return self.history.entries

    def clear_history(self) -> None:
        self._caretaker.save(CalculatorMemento.from_history(self.history.entries))
        self.history.clear()
        logger.info("History cleared")

    def save_history(self) -> str:
        path = self.history.save()
        return str(path)

    def load_history(self) -> int:
        self._caretaker.save(CalculatorMemento.from_history(self.history.entries))
        loaded = self.history.load()
        self._caretaker.clear()  # reset undo/redo after loading history file
        return len(loaded)

    # Undo and redo

    def undo(self) -> bool:
        """Restore the previous history state. Returns True if undo succeeded."""
        current = CalculatorMemento.from_history(self.history.entries)
        previous = self._caretaker.undo(current)
        if previous is None:
            return False
        self.history.set_history(previous.get_history())
        logger.info("Undo performed; history size=%s", len(self.history))
        return True

    def redo(self) -> bool:
        """Re-apply an undone history state. Returns True if redo succeeded."""
        current = CalculatorMemento.from_history(self.history.entries)
        nxt = self._caretaker.redo(current)
        if nxt is None:
            return False
        self.history.set_history(nxt.get_history())
        logger.info("Redo performed; history size=%s", len(self.history))
        return True

    def available_operations(self) -> List[str]:
        return sorted(OperationFactory.available_operations().keys())
