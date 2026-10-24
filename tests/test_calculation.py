"""Tests for the Calculation model."""

from datetime import datetime, timezone

import pytest

from app.calculation import Calculation
from app.exceptions import OperationError


def test_create_calculation():
    calc = Calculation.create("add", 2, 3, precision=2)
    assert calc.operation == "add"
    assert calc.operand1 == 2
    assert calc.operand2 == 3
    assert calc.result == 5
    assert isinstance(calc.timestamp, datetime)


def test_create_with_precision():
    calc = Calculation.create("divide", 1, 3, precision=4)
    assert calc.result == 0.3333


def test_create_operation_error():
    with pytest.raises(OperationError):
        Calculation.create("divide", 1, 0)


def test_to_from_dict_roundtrip():
    original = Calculation.create("multiply", 4, 5)
    data = original.to_dict()
    restored = Calculation.from_dict(data)
    assert restored.operation == original.operation
    assert restored.operand1 == original.operand1
    assert restored.operand2 == original.operand2
    assert restored.result == original.result
    assert restored.timestamp == original.timestamp


def test_from_dict_with_datetime_object():
    ts = datetime.now(timezone.utc)
    calc = Calculation.from_dict(
        {
            "operation": "add",
            "operand1": 1,
            "operand2": 2,
            "result": 3,
            "timestamp": ts,
        }
    )
    assert calc.timestamp == ts


def test_from_dict_missing_timestamp():
    calc = Calculation.from_dict(
        {
            "operation": "add",
            "operand1": 1,
            "operand2": 2,
            "result": 3,
            "timestamp": None,
        }
    )
    assert calc.result == 3


def test_str_representation():
    calc = Calculation.create("subtract", 9, 4)
    assert str(calc) == "subtract(9, 4) = 5"
