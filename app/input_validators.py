"""Input validation helpers for calculator operands and commands."""

from __future__ import annotations

from typing import Tuple

from app.exceptions import ValidationError


def parse_number(value: str, max_input_value: float) -> float:
    """Parse a string into a float and enforce the configured magnitude limit."""
    text = value.strip()
    if not text:
        raise ValidationError("Numeric input cannot be empty")
    try:
        number = float(text)
    except ValueError as exc:
        raise ValidationError(f"Invalid number: {value!r}") from exc

    if abs(number) > max_input_value:
        raise ValidationError(
            f"Value {number} exceeds maximum allowed input "
            f"({max_input_value})"
        )
    return number


def parse_two_operands(
    args: list[str], max_input_value: float
) -> Tuple[float, float]:
    """Validate that exactly two numerical operands were provided."""
    if len(args) != 2:
        raise ValidationError(
            f"Expected exactly 2 operands, got {len(args)}. "
            "Usage: <operation> <number1> <number2>"
        )
    a = parse_number(args[0], max_input_value)
    b = parse_number(args[1], max_input_value)
    return a, b


def require_non_empty(command_line: str) -> str:
    """Strip and require a non-empty command line."""
    stripped = command_line.strip()
    if not stripped:
        raise ValidationError("Please enter a command (type 'help' for options)")
    return stripped
