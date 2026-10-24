"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.logger import reset_logging_for_tests


@pytest.fixture
def tmp_config(tmp_path: Path) -> CalculatorConfig:
    """Config fixture writing logs and history to a temp directory."""
    reset_logging_for_tests()
    log_dir = tmp_path / "logs"
    history_dir = tmp_path / "history"
    log_dir.mkdir()
    history_dir.mkdir()
    return CalculatorConfig(
        log_dir=log_dir,
        history_dir=history_dir,
        log_file=log_dir / "calculator.log",
        history_file=history_dir / "calculation_history.csv",
        max_history_size=5,
        auto_save=False,
        precision=6,
        max_input_value=1_000_000,
        default_encoding="utf-8",
    )


@pytest.fixture
def calculator(tmp_config: CalculatorConfig) -> Calculator:
    """Calculator instance with auto-save disabled for testing."""
    return Calculator(config=tmp_config)


@pytest.fixture
def autosave_calculator(tmp_path: Path) -> Calculator:
    """Calculator with auto-save enabled."""
    reset_logging_for_tests()
    log_dir = tmp_path / "logs"
    history_dir = tmp_path / "history"
    log_dir.mkdir()
    history_dir.mkdir()
    config = CalculatorConfig(
        log_dir=log_dir,
        history_dir=history_dir,
        log_file=log_dir / "calculator.log",
        history_file=history_dir / "calculation_history.csv",
        max_history_size=10,
        auto_save=True,
        precision=4,
        max_input_value=1000,
        default_encoding="utf-8",
    )
    return Calculator(config=config)
