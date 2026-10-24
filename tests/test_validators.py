"""Tests for input validators."""

import pytest

from app.exceptions import ValidationError
from app.input_validators import parse_number, parse_two_operands, require_non_empty


def test_parse_number_valid():
    assert parse_number("3.14", 100) == 3.14
    assert parse_number("-2", 100) == -2


def test_parse_number_invalid():
    with pytest.raises(ValidationError):
        parse_number("abc", 100)
    with pytest.raises(ValidationError):
        parse_number("", 100)
    with pytest.raises(ValidationError):
        parse_number("9999", 100)


def test_parse_two_operands():
    assert parse_two_operands(["1", "2"], 100) == (1.0, 2.0)
    with pytest.raises(ValidationError, match="exactly 2"):
        parse_two_operands(["1"], 100)
    with pytest.raises(ValidationError, match="exactly 2"):
        parse_two_operands(["1", "2", "3"], 100)


def test_require_non_empty():
    assert require_non_empty("  help  ") == "help"
    with pytest.raises(ValidationError):
        require_non_empty("   ")
