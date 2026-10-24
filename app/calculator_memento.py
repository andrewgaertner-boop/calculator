"""Memento pattern implementation for calculator history."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import List

from app.calculation import Calculation


@dataclass
class CalculatorMemento:
    """Snapshot of calculator history at a point in time."""

    history: List[Calculation] = field(default_factory=list)

    @classmethod
    def from_history(cls, history: List[Calculation]) -> "CalculatorMemento":
        """Create a memento containing a copy of the given history."""
        return cls(history=deepcopy(history))

    def get_history(self) -> List[Calculation]:
        """Return a deep copy of the stored history."""
        return deepcopy(self.history)


class Caretaker:
    """Manages undo and redo stacks of CalculatorMemento instances."""

    def __init__(self) -> None:
        self._undo_stack: List[CalculatorMemento] = []
        self._redo_stack: List[CalculatorMemento] = []

    def save(self, memento: CalculatorMemento) -> None:
        """Push a new state and clear the redo stack."""
        self._undo_stack.append(memento)
        self._redo_stack.clear()

    def undo(self, current: CalculatorMemento) -> CalculatorMemento | None:
        """
        Undo to the previous state.

        Saves current state onto the redo stack and returns the previous state,
        or None if nothing can be undone.
        """
        if not self._undo_stack:
            return None
        self._redo_stack.append(current)
        return self._undo_stack.pop()

    def redo(self, current: CalculatorMemento) -> CalculatorMemento | None:
        """
        Redo a previously undone state.

        Saves current state onto the undo stack and returns the next state,
        or None if nothing can be redone.
        """
        if not self._redo_stack:
            return None
        self._undo_stack.append(current)
        return self._redo_stack.pop()

    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    def can_redo(self) -> bool:
        return bool(self._redo_stack)

    def clear(self) -> None:
        """Clear both undo and redo stacks."""
        self._undo_stack.clear()
        self._redo_stack.clear()
