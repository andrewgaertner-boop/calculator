"""Calculation model representing a single arithmetic computation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict

from app.exceptions import OperationError
from app.operations import Operation, OperationFactory


@dataclass
class Calculation:
    """A completed (or pending) calculation with operands and result."""

    operation: str
    operand1: float
    operand2: float
    result: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        operation_name: str,
        operand1: float,
        operand2: float,
        operation: Operation | None = None,
        precision: int | None = None,
    ) -> "Calculation":
        """Create and execute a calculation using the given operation."""
        op = operation or OperationFactory.create(operation_name)
        try:
            raw_result = op.execute(operand1, operand2)
        except OperationError:
            raise
        except Exception as exc:  # pragma: no cover
            raise OperationError(f"Operation failed: {exc}") from exc

        if precision is not None:
            raw_result = round(raw_result, precision)

        return cls(
            operation=op.name,
            operand1=operand1,
            operand2=operand2,
            result=raw_result,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert calculation fields to a dictionary for CSV storage."""
        return {
            "operation": self.operation,
            "operand1": self.operand1,
            "operand2": self.operand2,
            "result": self.result,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Calculation":
        """Create a Calculation instance from a dictionary row."""
        timestamp_raw = data.get("timestamp")
        if isinstance(timestamp_raw, datetime):
            timestamp = timestamp_raw
        elif timestamp_raw is None or timestamp_raw == "":
            timestamp = datetime.now(timezone.utc)
        else:
            timestamp = datetime.fromisoformat(str(timestamp_raw))

        return cls(
            operation=str(data["operation"]),
            operand1=float(data["operand1"]),
            operand2=float(data["operand2"]),
            result=float(data["result"]),
            timestamp=timestamp,
        )

    def __str__(self) -> str:
        return (
            f"{self.operation}({self.operand1}, {self.operand2}) = {self.result}"
        )
