"""Arithmetic operations and Factory for creating operation instances."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Type

from app.exceptions import OperationError


class Operation(ABC):
    """Abstract base class for binary arithmetic operations."""

    name: str = "operation"
    symbol: str = "?"

    @abstractmethod
    def execute(self, a: float, b: float) -> float:
        """Execute the operation with operands a and b."""

    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.__class__.__name__}()"


class Add(Operation):
    name = "add"
    symbol = "+"

    def execute(self, a: float, b: float) -> float:
        return a + b


class Subtract(Operation):
    name = "subtract"
    symbol = "-"

    def execute(self, a: float, b: float) -> float:
        return a - b


class Multiply(Operation):
    name = "multiply"
    symbol = "*"

    def execute(self, a: float, b: float) -> float:
        return a * b


class Divide(Operation):
    name = "divide"
    symbol = "/"

    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise OperationError("Division by zero is not allowed")
        return a / b


class Power(Operation):
    name = "power"
    symbol = "^"

    def execute(self, a: float, b: float) -> float:
        try:
            return a**b
        except OverflowError as exc:
            raise OperationError("Result overflowed for power operation") from exc


class Root(Operation):
    """Compute the b-th root of a (root(a, b) => a ** (1/b))."""

    name = "root"
    symbol = "√"

    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise OperationError("Root degree cannot be zero")
        if a < 0 and abs(b) % 2 == 0:
            raise OperationError("Even root of a negative number is not defined")
        try:
            # Handle negative bases with odd roots via sign preservation
            if a < 0:
                return -((-a) ** (1.0 / b))
            return a ** (1.0 / b)
        except (OverflowError, ZeroDivisionError, ValueError) as exc:
            raise OperationError(f"Unable to compute root: {exc}") from exc


class Modulus(Operation):
    name = "modulus"
    symbol = "%"

    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise OperationError("Modulus by zero is not allowed")
        return a % b


class IntegerDivide(Operation):
    name = "int_divide"
    symbol = "//"

    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise OperationError("Integer division by zero is not allowed")
        return a // b


class Percentage(Operation):
    """Percentage of a with respect to b: (a / b) * 100."""

    name = "percent"
    symbol = "pct"

    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise OperationError("Percentage with respect to zero is not allowed")
        return (a / b) * 100.0


class AbsoluteDifference(Operation):
    name = "abs_diff"
    symbol = "|a-b|"

    def execute(self, a: float, b: float) -> float:
        return abs(a - b)


class OperationFactory:
    """Factory for creating operation instances by name."""

    _registry: Dict[str, Type[Operation]] = {
        "add": Add,
        "subtract": Subtract,
        "multiply": Multiply,
        "divide": Divide,
        "power": Power,
        "root": Root,
        "modulus": Modulus,
        "int_divide": IntegerDivide,
        "percent": Percentage,
        "abs_diff": AbsoluteDifference,
    }

    @classmethod
    def register(cls, name: str, operation_cls: Type[Operation]) -> None:
        """Register a new operation type with the factory."""
        cls._registry[name.lower()] = operation_cls

    @classmethod
    def create(cls, name: str) -> Operation:
        """Create an operation instance by command name."""
        key = name.lower().strip()
        if key not in cls._registry:
            available = ", ".join(sorted(cls._registry))
            raise OperationError(
                f"Unknown operation '{name}'. Available operations: {available}"
            )
        return cls._registry[key]()

    @classmethod
    def available_operations(cls) -> Dict[str, Type[Operation]]:
        """Return a copy of the registered operations map."""
        return dict(cls._registry)
