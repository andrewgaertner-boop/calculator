"""Tests for arithmetic operations and the OperationFactory."""

import math

import pytest

from app.exceptions import OperationError
from app.operations import (
    AbsoluteDifference,
    Add,
    Divide,
    IntegerDivide,
    Modulus,
    Multiply,
    OperationFactory,
    Percentage,
    Power,
    Root,
    Subtract,
)


@pytest.mark.parametrize(
    "op_cls,a,b,expected",
    [
        (Add, 2, 3, 5),
        (Subtract, 10, 4, 6),
        (Multiply, 3, 4, 12),
        (Divide, 10, 4, 2.5),
        (Power, 2, 3, 8),
        (Power, 9, 0.5, 3),
        (Root, 27, 3, 3),
        (Root, 16, 2, 4),
        (Modulus, 10, 3, 1),
        (IntegerDivide, 10, 3, 3),
        (Percentage, 25, 50, 50),
        (AbsoluteDifference, 10, 3, 7),
        (AbsoluteDifference, 3, 10, 7),
    ],
)
def test_operations_execute(op_cls, a, b, expected):
    result = op_cls().execute(a, b)
    assert math.isclose(result, expected, rel_tol=1e-9)


@pytest.mark.parametrize(
    "op_cls,a,b",
    [
        (Divide, 1, 0),
        (Modulus, 5, 0),
        (IntegerDivide, 5, 0),
        (Percentage, 5, 0),
        (Root, 8, 0),
        (Root, -16, 2),
    ],
)
def test_operations_errors(op_cls, a, b):
    with pytest.raises(OperationError):
        op_cls().execute(a, b)


def test_root_negative_odd_degree():
    result = Root().execute(-8, 3)
    assert math.isclose(result, -2, rel_tol=1e-9)


def test_factory_create_known():
    op = OperationFactory.create("add")
    assert isinstance(op, Add)
    assert op.execute(1, 2) == 3


def test_factory_create_unknown():
    with pytest.raises(OperationError, match="Unknown operation"):
        OperationFactory.create("noop")


def test_factory_register_custom():
    class DoubleAdd(Add):
        name = "double_add"

        def execute(self, a, b):
            return (a + b) * 2

    OperationFactory.register("double_add", DoubleAdd)
    op = OperationFactory.create("double_add")
    assert op.execute(2, 3) == 10
    # Clean up custom test registration
    del OperationFactory._registry["double_add"]


def test_available_operations_contains_mandatory():
    available = OperationFactory.available_operations()
    for name in (
        "power",
        "root",
        "modulus",
        "int_divide",
        "percent",
        "abs_diff",
    ):
        assert name in available


def test_power_overflow():
    with pytest.raises(OperationError, match="overflow"):
        Power().execute(10.0**100, 10.0**100)
