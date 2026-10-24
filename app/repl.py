"""Command-line interface (REPL) for the calculator with colorama output."""

from __future__ import annotations

from typing import Callable, List, Optional

from colorama import Fore, Style, init as colorama_init

from app.calculator import Calculator
from app.exceptions import CalculatorError, HistoryError, ValidationError
from app.input_validators import parse_two_operands, require_non_empty
from app.logger import get_logger
from app.operations import OperationFactory

logger = get_logger("repl")


def build_help_menu() -> str:
    """Return the formatted help text including available operations."""
    lines = [
        "Calculator Commands:",
        "  history              Show calculation history",
        "  clear                Clear calculation history",
        "  undo                 Undo the last calculation",
        "  redo                 Redo the last undone calculation",
        "  save                 Save history to CSV",
        "  load                 Load history from CSV",
        "  help                 Show this help menu",
        "  exit                 Exit the application",
        "  Arithmetic operations (usage: <op> <n1> <n2>):",
    ]
    for name, cls in sorted(OperationFactory.available_operations().items()):
        symbol = getattr(cls, "symbol", "?")
        lines.append(f"    {name:<12} ({symbol})")
    return "\n".join(lines) + "\n"


def execute_command(calculator: Calculator, tokens: List[str]) -> tuple[str, bool]:
    """Execute a single tokenized command and return (message, is_exit)."""
    cmd = tokens[0].lower()
    args = tokens[1:]

    if cmd in ("exit", "quit"):
        return "Goodbye!", True

    if cmd == "help":
        return build_help_menu(), False

    if cmd == "history":
        entries = calculator.get_history()
        if not entries:
            return "History is empty.", False
        lines = ["Calculation History:"]
        for idx, calc in enumerate(entries, start=1):
            lines.append(f"  {idx}. {calc}")
        return "\n".join(lines), False

    if cmd == "clear":
        calculator.clear_history()
        return "History cleared.", False

    if cmd == "undo":
        if calculator.undo():
            return "Undo successful.", False
        return "Nothing to undo.", False

    if cmd == "redo":
        if calculator.redo():
            return "Redo successful.", False
        return "Nothing to redo.", False

    if cmd == "save":
        path = calculator.save_history()
        return f"History saved to {path}", False

    if cmd == "load":
        count = calculator.load_history()
        return f"Loaded {count} calculation(s) from history file.", False

    if cmd in OperationFactory.available_operations():
        a, b = parse_two_operands(args, calculator.config.max_input_value)
        result = calculator.calculate(cmd, a, b)
        return f"Result: {result.result}", False

    raise ValidationError(
        f"Unknown command '{cmd}'. Type 'help' to see available commands."
    )


def _colorize(message: str, color: str) -> str:
    return f"{color}{message}{Style.RESET_ALL}"


def run_repl(
    calculator: Optional[Calculator] = None,
    input_func: Callable[[str], str] = input,
    output_func: Callable[[str], None] = print,
) -> None:
    """Start the Read-Eval-Print Loop with Colorama color-coded output."""
    colorama_init(autoreset=True)
    calc = calculator or Calculator()

    output_func(_colorize("Enhanced Calculator REPL", Fore.CYAN))
    output_func(_colorize("Type 'help' for commands, 'exit' to quit.", Fore.CYAN))

    while True:
        try:
            raw = input_func("> ")
            line = require_non_empty(raw)
            tokens = line.split()
            message, is_exit = execute_command(calc, tokens)
            if is_exit:
                output_func(_colorize(message, Fore.CYAN))
                logger.info("Application exited by user")
                break
            color = Fore.GREEN if message.startswith("Result:") else Fore.WHITE
            output_func(_colorize(message, color))
        except ValidationError as exc:
            output_func(_colorize(f"Validation error: {exc}", Fore.YELLOW))
            logger.warning("Validation error: %s", exc)
        except HistoryError as exc:
            output_func(_colorize(f"History error: {exc}", Fore.RED))
            logger.error("History error: %s", exc)
        except CalculatorError as exc:
            output_func(_colorize(f"Error: {exc}", Fore.RED))
            logger.error("Calculator error: %s", exc)
        except (EOFError, KeyboardInterrupt):  # pragma: no cover
            output_func("")
            output_func(_colorize("Goodbye!", Fore.CYAN))
            break
