"""Tests for Calculator, observers, undo/redo, and persistence."""

from pathlib import Path

import pandas as pd
import pytest

from app.calculator import AutoSaveObserver, Calculator, LoggingObserver, Observer
from app.calculation import Calculation
from app.exceptions import HistoryError, OperationError
from app.logger import reset_logging_for_tests


def test_basic_calculate(calculator: Calculator):
    calc = calculator.calculate("add", 2, 3)
    assert calc.result == 5
    assert len(calculator.get_history()) == 1


def test_calculate_failure_does_not_pollute_history(calculator: Calculator):
    with pytest.raises(OperationError):
        calculator.calculate("divide", 1, 0)
    assert calculator.get_history() == []
    assert calculator.undo() is False


def test_undo_redo(calculator: Calculator):
    calculator.calculate("add", 1, 1)
    calculator.calculate("multiply", 2, 3)
    assert len(calculator.get_history()) == 2

    assert calculator.undo() is True
    assert len(calculator.get_history()) == 1
    assert calculator.get_history()[0].result == 2

    assert calculator.redo() is True
    assert len(calculator.get_history()) == 2

    assert calculator.redo() is False


def test_clear_history_and_undo(calculator: Calculator):
    calculator.calculate("add", 1, 2)
    calculator.clear_history()
    assert calculator.get_history() == []
    assert calculator.undo() is True
    assert len(calculator.get_history()) == 1


def test_save_and_load_history(calculator: Calculator, tmp_config):
    calculator.calculate("power", 2, 3)
    calculator.calculate("percent", 25, 50)
    path = calculator.save_history()
    assert Path(path).exists()

    df = pd.read_csv(path)
    assert list(df.columns) == [
        "operation",
        "operand1",
        "operand2",
        "result",
        "timestamp",
    ]
    assert len(df) == 2

    calculator.clear_history()
    # Verify load replaces history
    loaded = calculator.load_history()
    assert loaded == 2
    assert calculator.get_history()[0].result == 8


def test_load_missing_file(calculator: Calculator):
    with pytest.raises(HistoryError, match="not found"):
        calculator.load_history()


def test_load_malformed_file(calculator: Calculator, tmp_config):
    bad = tmp_config.history_file
    bad.write_text("not,a,valid\ncsv", encoding="utf-8")
    with pytest.raises(HistoryError):
        calculator.load_history()


def test_max_history_size(calculator: Calculator):
    for i in range(7):
        calculator.calculate("add", i, 1)
    assert len(calculator.get_history()) == 5
    assert calculator.get_history()[0].operand1 == 2


def test_precision_applied(calculator: Calculator):
    calc = calculator.calculate("divide", 1, 3)
    assert calc.result == 0.333333  # precision=6


def test_autosave_observer(autosave_calculator: Calculator):
    autosave_calculator.calculate("add", 1, 2)
    assert autosave_calculator.config.history_file.exists()
    df = pd.read_csv(autosave_calculator.config.history_file)
    assert len(df) == 1


def test_observer_registration(calculator: Calculator):
    class Spy(Observer):
        def __init__(self):
            self.seen = []

        def update(self, calculation, calc):
            self.seen.append(calculation)

    spy = Spy()
    calculator.add_observer(spy)
    calculator.calculate("add", 1, 1)
    assert len(spy.seen) == 1
    calculator.remove_observer(spy)
    calculator.calculate("add", 2, 2)
    assert len(spy.seen) == 1


def test_available_operations(calculator: Calculator):
    ops = calculator.available_operations()
    assert "root" in ops
    assert ops == sorted(ops)


def test_logging_observer_does_not_raise(calculator: Calculator):
    # LoggingObserver is registered by default
    assert any(isinstance(o, LoggingObserver) for o in calculator._observers)
    calculator.calculate("abs_diff", 10, 3)


def test_autosave_failure_is_logged(tmp_path, monkeypatch):
    reset_logging_for_tests()
    from app.calculator_config import CalculatorConfig

    config = CalculatorConfig(
        log_dir=tmp_path / "logs",
        history_dir=tmp_path / "history",
        log_file=tmp_path / "logs" / "calculator.log",
        history_file=tmp_path / "history" / "calculation_history.csv",
        max_history_size=5,
        auto_save=True,
        precision=2,
        max_input_value=100,
        default_encoding="utf-8",
    )
    config.ensure_directories()
    calc = Calculator(config=config)

    def boom(*_args, **_kwargs):
        raise HistoryError("disk full")

    monkeypatch.setattr(calc.history, "save", boom)
    # Should not raise; AutoSaveObserver catches HistoryError
    result = calc.calculate("add", 1, 1)
    assert result.result == 2
