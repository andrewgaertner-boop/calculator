"""Tests for HistoryManager."""

from pathlib import Path

import pytest

from app.calculation import Calculation
from app.exceptions import HistoryError
from app.history import HistoryManager


def test_history_add_clear_dataframe(tmp_path: Path):
    manager = HistoryManager(tmp_path / "h.csv", max_size=3)
    assert len(manager) == 0
    df_empty = manager.to_dataframe()
    assert list(df_empty.columns) == HistoryManager.COLUMNS
    assert df_empty.empty

    manager.add(Calculation.create("add", 1, 1))
    manager.add(Calculation.create("add", 2, 2))
    assert len(manager) == 2
    assert not manager.to_dataframe().empty

    manager.clear()
    assert len(manager) == 0


def test_history_trimming(tmp_path: Path):
    manager = HistoryManager(tmp_path / "h.csv", max_size=2)
    manager.add(Calculation.create("add", 1, 0))
    manager.add(Calculation.create("add", 2, 0))
    manager.add(Calculation.create("add", 3, 0))
    assert len(manager) == 2
    assert manager.entries[0].operand1 == 2


def test_save_load_roundtrip(tmp_path: Path):
    path = tmp_path / "h.csv"
    manager = HistoryManager(path, max_size=10)
    manager.add(Calculation.create("multiply", 3, 4))
    manager.save()

    other = HistoryManager(path, max_size=10)
    loaded = other.load()
    assert len(loaded) == 1
    assert loaded[0].result == 12


def test_load_missing(tmp_path: Path):
    manager = HistoryManager(tmp_path / "missing.csv", max_size=5)
    with pytest.raises(HistoryError, match="not found"):
        manager.load()


def test_load_malformed_columns(tmp_path: Path):
    path = tmp_path / "bad.csv"
    path.write_text("foo,bar\n1,2\n", encoding="utf-8")
    manager = HistoryManager(path, max_size=5)
    with pytest.raises(HistoryError, match="missing columns"):
        manager.load()


def test_set_history_trims(tmp_path: Path):
    manager = HistoryManager(tmp_path / "h.csv", max_size=2)
    manager.set_history(
        [
            Calculation.create("add", 1, 0),
            Calculation.create("add", 2, 0),
            Calculation.create("add", 3, 0),
        ]
    )
    assert len(manager) == 2
    assert manager.entries[0].operand1 == 2


def test_save_failure(tmp_path: Path, monkeypatch):
    manager = HistoryManager(tmp_path / "h.csv", max_size=5)
    manager.add(Calculation.create("add", 1, 1))

    def boom(*_a, **_k):
        raise OSError("denied")

    monkeypatch.setattr("pandas.DataFrame.to_csv", boom)
    with pytest.raises(HistoryError, match="Failed to save"):
        manager.save()


def test_load_unreadable_file(tmp_path: Path, monkeypatch):
    path = tmp_path / "h.csv"
    path.write_text(
        "operation,operand1,operand2,result,timestamp\n", encoding="utf-8"
    )
    manager = HistoryManager(path, max_size=5)

    def boom(*_a, **_k):
        raise OSError("denied")

    monkeypatch.setattr("pandas.read_csv", boom)
    with pytest.raises(HistoryError, match="Failed to read"):
        manager.load()


def test_load_bad_row_data(tmp_path: Path):
    path = tmp_path / "h.csv"
    path.write_text(
        "operation,operand1,operand2,result,timestamp\n"
        "add,not-a-number,2,3,2020-01-01T00:00:00+00:00\n",
        encoding="utf-8",
    )
    manager = HistoryManager(path, max_size=5)
    with pytest.raises(HistoryError, match="Malformed history data"):
        manager.load()
