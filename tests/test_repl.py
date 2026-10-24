"""Tests for the REPL and command execution."""

import pytest

from app.calculator import Calculator
from app.exceptions import ValidationError
from app.repl import (
    build_help_menu,
    execute_command,
    run_repl,
)


def test_build_help_includes_operations():
    help_text = build_help_menu()
    assert "history" in help_text
    assert "power" in help_text
    assert "abs_diff" in help_text
    assert "exit" in help_text


def test_execute_command_operations(calculator: Calculator):
    msg, is_exit = execute_command(calculator, ["add", "2", "3"])
    assert is_exit is False
    assert "Result: 5" in msg


def test_execute_command_meta(calculator: Calculator):
    calculator.calculate("add", 1, 1)

    msg, is_exit = execute_command(calculator, ["history"])
    assert is_exit is False
    assert "add" in msg

    msg, is_exit = execute_command(calculator, ["undo"])
    assert is_exit is False
    assert "successful" in msg.lower()

    msg, is_exit = execute_command(calculator, ["redo"])
    assert is_exit is False
    assert "successful" in msg.lower()

    msg, is_exit = execute_command(calculator, ["clear"])
    assert is_exit is False
    assert "cleared" in msg.lower()

    msg, is_exit = execute_command(calculator, ["help"])
    assert is_exit is False
    assert "Calculator Commands" in msg

    msg, is_exit = execute_command(calculator, ["exit"])
    assert is_exit is True
    assert "Goodbye" in msg

    msg, is_exit = execute_command(calculator, ["quit"])
    assert is_exit is True
    assert "Goodbye" in msg


def test_execute_command_unknown(calculator: Calculator):
    with pytest.raises(ValidationError, match="Unknown command"):
        execute_command(calculator, ["invalid_command"])


def test_save_load_commands(calculator: Calculator):
    calculator.calculate("add", 4, 5)
    save_msg, _ = execute_command(calculator, ["save"])
    assert "saved" in save_msg.lower()

    execute_command(calculator, ["clear"])
    load_msg, _ = execute_command(calculator, ["load"])
    assert "Loaded 1" in load_msg


def test_undo_redo_empty_messages(calculator: Calculator):
    msg_undo, _ = execute_command(calculator, ["undo"])
    assert "Nothing to undo" in msg_undo

    msg_redo, _ = execute_command(calculator, ["redo"])
    assert "Nothing to redo" in msg_redo

    msg_hist, _ = execute_command(calculator, ["history"])
    assert "empty" in msg_hist.lower()


def test_run_repl_flow(calculator: Calculator):
    inputs = iter(
        [
            "help",
            "add 2 3",
            "history",
            "undo",
            "redo",
            "save",
            "clear",
            "load",
            "divide 1 0",
            "bogus",
            "add 1",
            "",
            "exit",
        ]
    )
    outputs: list[str] = []

    def fake_input(_prompt: str = "") -> str:
        return next(inputs)

    run_repl(
        calculator=calculator,
        input_func=fake_input,
        output_func=outputs.append,
    )

    joined = "\n".join(outputs)
    assert "Enhanced Calculator REPL" in joined
    assert "Result: 5" in joined
    assert "Goodbye!" in joined
    assert "Validation error" in joined or "Error:" in joined
