"""Tests for the Memento caretaker."""

from app.calculation import Calculation
from app.calculator_memento import CalculatorMemento, Caretaker


def test_memento_deepcopy_isolation():
    calc = Calculation.create("add", 1, 2)
    history = [calc]
    memento = CalculatorMemento.from_history(history)
    history.clear()
    assert len(memento.get_history()) == 1


def test_caretaker_undo_redo_empty():
    caretaker = Caretaker()
    current = CalculatorMemento.from_history([])
    assert caretaker.undo(current) is None
    assert caretaker.redo(current) is None
    assert caretaker.can_undo() is False
    assert caretaker.can_redo() is False


def test_caretaker_flow():
    caretaker = Caretaker()
    state0 = CalculatorMemento.from_history([])
    state1 = CalculatorMemento.from_history([Calculation.create("add", 1, 1)])
    state2 = CalculatorMemento.from_history(
        [
            Calculation.create("add", 1, 1),
            Calculation.create("add", 2, 2),
        ]
    )

    caretaker.save(state0)
    caretaker.save(state1)

    restored = caretaker.undo(state2)
    assert restored is not None
    assert len(restored.get_history()) == 1

    redone = caretaker.redo(restored)
    assert redone is not None
    assert len(redone.get_history()) == 2

    caretaker.clear()
    assert caretaker.can_undo() is False
    assert caretaker.can_redo() is False
