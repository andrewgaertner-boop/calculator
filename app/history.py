"""History management with pandas-backed CSV persistence."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import pandas as pd

from app.calculation import Calculation
from app.exceptions import HistoryError
from app.logger import get_logger

logger = get_logger("history")


class HistoryManager:
    """Stores calculations and persists them to CSV via pandas."""

    COLUMNS = ["operation", "operand1", "operand2", "result", "timestamp"]

    def __init__(
        self,
        history_file: Path,
        max_size: int,
        encoding: str = "utf-8",
    ) -> None:
        self._history: List[Calculation] = []
        self.history_file = Path(history_file)
        self.max_size = max_size
        self.encoding = encoding

    @property
    def entries(self) -> List[Calculation]:
        """Return a copy of the calculation history entries."""
        return list(self._history)

    def __len__(self) -> int:
        return len(self._history)

    def add(self, calculation: Calculation) -> None:
        """Add a calculation, trimming older entries if exceeding max size."""
        self._history.append(calculation)
        while len(self._history) > self.max_size:
            self._history.pop(0)

    def clear(self) -> None:
        """Remove all in-memory history entries."""
        self._history.clear()

    def set_history(self, calculations: List[Calculation]) -> None:
        """Set the current history to a new list of calculations."""
        self._history = list(calculations)
        while len(self._history) > self.max_size:
            self._history.pop(0)

    def to_dataframe(self) -> pd.DataFrame:
        """Convert history to a pandas DataFrame."""
        if not self._history:
            return pd.DataFrame(columns=self.COLUMNS)
        rows = [calc.to_dict() for calc in self._history]
        return pd.DataFrame(rows, columns=self.COLUMNS)

    def save(self, path: Optional[Path] = None) -> Path:
        """Serialize history to CSV using pandas."""
        target = Path(path) if path is not None else self.history_file
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            df = self.to_dataframe()
            df.to_csv(target, index=False, encoding=self.encoding)
            logger.info("Saved %s history entries to %s", len(self._history), target)
            return target
        except Exception as exc:
            raise HistoryError(f"Failed to save history to {target}: {exc}") from exc

    def load(self, path: Optional[Path] = None) -> List[Calculation]:
        """Deserialize history from CSV using pandas and replace in-memory state."""
        target = Path(path) if path is not None else self.history_file
        if not target.exists():
            raise HistoryError(f"History file not found: {target}")
        try:
            df = pd.read_csv(target, encoding=self.encoding)
        except Exception as exc:
            raise HistoryError(f"Failed to read history file {target}: {exc}") from exc

        missing = [col for col in self.COLUMNS if col not in df.columns]
        if missing:
            raise HistoryError(
                f"Malformed history file; missing columns: {', '.join(missing)}"
            )

        calculations: List[Calculation] = []
        try:
            for _, row in df.iterrows():
                calculations.append(Calculation.from_dict(row.to_dict()))
        except Exception as exc:
            raise HistoryError(
                f"Malformed history data in {target}: {exc}"
            ) from exc

        self.set_history(calculations)
        logger.info("Loaded %s history entries from %s", len(calculations), target)
        return self.entries
