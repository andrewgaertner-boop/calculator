"""Configuration management loaded from environment variables / .env file."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from app.exceptions import ConfigurationError


@dataclass(frozen=True)
class CalculatorConfig:
    """Immutable configuration for the calculator application."""

    log_dir: Path
    history_dir: Path
    log_file: Path
    history_file: Path
    max_history_size: int
    auto_save: bool
    precision: int
    max_input_value: float
    default_encoding: str

    def ensure_directories(self) -> None:
        """Create log and history directories if they do not exist."""
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)


def _parse_bool(value: str, name: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "on"}:
        return True
    if normalized in {"false", "0", "no", "off"}:
        return False
    raise ConfigurationError(
        f"Invalid boolean value for {name}: {value!r}. Use true or false."
    )


def _parse_int(value: str, name: str, minimum: int = 0) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ConfigurationError(f"Invalid integer for {name}: {value!r}") from exc
    if parsed < minimum:
        raise ConfigurationError(f"{name} must be >= {minimum}, got {parsed}")
    return parsed


def _parse_float(value: str, name: str, minimum: float = 0.0) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ConfigurationError(f"Invalid number for {name}: {value!r}") from exc
    if parsed < minimum:
        raise ConfigurationError(f"{name} must be >= {minimum}, got {parsed}")
    return parsed


def load_config(env_path: str | Path | None = None) -> CalculatorConfig:
    """
    Load and validate calculator configuration from environment variables.

    Defaults are applied when variables are unset. Values from a `.env` file
    are loaded when present.
    """
    if env_path is not None:
        load_dotenv(dotenv_path=env_path, override=False)
    else:
        load_dotenv(override=False)

    try:
        log_dir = Path(os.getenv("CALCULATOR_LOG_DIR", "logs"))
        history_dir = Path(os.getenv("CALCULATOR_HISTORY_DIR", "history"))

        log_file_name = os.getenv("CALCULATOR_LOG_FILE", "calculator.log")
        history_file_name = os.getenv(
            "CALCULATOR_HISTORY_FILE", "calculation_history.csv"
        )

        # Allow absolute paths for file settings; otherwise join with base dirs
        log_file = Path(log_file_name)
        if not log_file.is_absolute():
            log_file = log_dir / log_file_name

        history_file = Path(history_file_name)
        if not history_file.is_absolute():
            history_file = history_dir / history_file_name

        max_history_size = _parse_int(
            os.getenv("CALCULATOR_MAX_HISTORY_SIZE", "100"),
            "CALCULATOR_MAX_HISTORY_SIZE",
            minimum=1,
        )
        auto_save = _parse_bool(
            os.getenv("CALCULATOR_AUTO_SAVE", "true"),
            "CALCULATOR_AUTO_SAVE",
        )
        precision = _parse_int(
            os.getenv("CALCULATOR_PRECISION", "6"),
            "CALCULATOR_PRECISION",
            minimum=0,
        )
        max_input_value = _parse_float(
            os.getenv("CALCULATOR_MAX_INPUT_VALUE", "1000000"),
            "CALCULATOR_MAX_INPUT_VALUE",
            minimum=0.0,
        )
        default_encoding = os.getenv("CALCULATOR_DEFAULT_ENCODING", "utf-8")
        if not default_encoding:
            raise ConfigurationError("CALCULATOR_DEFAULT_ENCODING cannot be empty")

        config = CalculatorConfig(
            log_dir=log_dir,
            history_dir=history_dir,
            log_file=log_file,
            history_file=history_file,
            max_history_size=max_history_size,
            auto_save=auto_save,
            precision=precision,
            max_input_value=max_input_value,
            default_encoding=default_encoding,
        )
        config.ensure_directories()
        return config
    except ConfigurationError:
        raise
    except Exception as exc:  # pragma: no cover
        raise ConfigurationError(f"Failed to load configuration: {exc}") from exc
