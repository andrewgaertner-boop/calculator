"""Tests for configuration loading and validation."""

import os
from pathlib import Path

import pytest

from app.calculator_config import load_config
from app.exceptions import ConfigurationError


def test_load_config_defaults(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # Clear relevant env vars
    for key in list(os.environ):
        if key.startswith("CALCULATOR_"):
            monkeypatch.delenv(key, raising=False)

    config = load_config(env_path=tmp_path / "missing.env")
    assert config.log_dir == Path("logs")
    assert config.history_dir == Path("history")
    assert config.max_history_size == 100
    assert config.auto_save is True
    assert config.precision == 6
    assert config.max_input_value == 1_000_000
    assert config.default_encoding == "utf-8"
    assert config.log_dir.exists()
    assert config.history_dir.exists()


def test_load_config_from_env_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for key in list(os.environ):
        if key.startswith("CALCULATOR_"):
            monkeypatch.delenv(key, raising=False)

    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "CALCULATOR_LOG_DIR=mylogs",
                "CALCULATOR_HISTORY_DIR=myhistory",
                "CALCULATOR_LOG_FILE=app.log",
                "CALCULATOR_HISTORY_FILE=hist.csv",
                "CALCULATOR_MAX_HISTORY_SIZE=10",
                "CALCULATOR_AUTO_SAVE=false",
                "CALCULATOR_PRECISION=2",
                "CALCULATOR_MAX_INPUT_VALUE=50",
                "CALCULATOR_DEFAULT_ENCODING=utf-8",
            ]
        ),
        encoding="utf-8",
    )
    config = load_config(env_path=env_file)
    assert config.log_dir == Path("mylogs")
    assert config.history_file == Path("myhistory") / "hist.csv"
    assert config.log_file == Path("mylogs") / "app.log"
    assert config.max_history_size == 10
    assert config.auto_save is False
    assert config.precision == 2
    assert config.max_input_value == 50


def test_invalid_bool(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "maybe")
    with pytest.raises(ConfigurationError, match="boolean"):
        load_config(env_path=tmp_path / "none.env")


def test_invalid_int(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CALCULATOR_PRECISION", "abc")
    with pytest.raises(ConfigurationError, match="integer"):
        load_config(env_path=tmp_path / "none.env")


def test_negative_max_history(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CALCULATOR_MAX_HISTORY_SIZE", "0")
    with pytest.raises(ConfigurationError):
        load_config(env_path=tmp_path / "none.env")


def test_empty_encoding(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CALCULATOR_DEFAULT_ENCODING", "")
    with pytest.raises(ConfigurationError, match="cannot be empty"):
        load_config(env_path=tmp_path / "none.env")


def test_bool_variants(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "YES")
    config = load_config(env_path=tmp_path / "none.env")
    assert config.auto_save is True

    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "off")
    config = load_config(env_path=tmp_path / "none.env")
    assert config.auto_save is False
