# Enhanced Calculator Command-Line Application

Advanced calculator with a Read-Eval-Print Loop (REPL), multiple arithmetic
operations, undo/redo, logging, CSV history persistence, and Continuous
Integration via GitHub Actions.

## Features

- **Arithmetic operations** (Factory pattern): `add`, `subtract`, `multiply`,
  `divide`, `power`, `root`, `modulus`, `int_divide`, `percent`, `abs_diff`
- **Undo / Redo** via the **Memento** design pattern
- **Observers**: `LoggingObserver` (file logging) and `AutoSaveObserver`
  (pandas CSV auto-save)
- **Configuration** via `.env` and `python-dotenv`
- **Optional feature**:
  - **Colorama** color-coded CLI output for enhanced readability (green results, yellow warnings, red errors, cyan prompts)

## Project Structure

```text
project_root/
├── app/
│   ├── __init__.py
│   ├── calculator.py
│   ├── calculation.py
│   ├── calculator_config.py
│   ├── calculator_memento.py
│   ├── exceptions.py
│   ├── history.py
│   ├── input_validators.py
│   ├── operations.py
│   ├── logger.py
│   ├── repl.py
│   └── __main__.py
├── tests/
├── .env
├── requirements.txt
├── README.md
├── main.py
└── .github/workflows/python-app.yml
```

## Installation

```bash
# Clone the repository, then:
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration (`.env`)

Copy or edit the provided `.env` file. Supported variables:

| Variable                        | Description                                            | Default                     |
| ------------------------------- | ------------------------------------------------------ | --------------------------- |
| `CALCULATOR_LOG_DIR`          | Directory for log files                                | `logs`                    |
| `CALCULATOR_HISTORY_DIR`      | Directory for history files                            | `history`                 |
| `CALCULATOR_LOG_FILE`         | Log file name (or absolute path)                       | `calculator.log`          |
| `CALCULATOR_HISTORY_FILE`     | History CSV name (or absolute path)                    | `calculation_history.csv` |
| `CALCULATOR_MAX_HISTORY_SIZE` | Max in-memory history entries                          | `100`                     |
| `CALCULATOR_AUTO_SAVE`        | Auto-save history after each calc (`true`/`false`) | `true`                    |
| `CALCULATOR_PRECISION`        | Decimal places for results                             | `6`                       |
| `CALCULATOR_MAX_INPUT_VALUE`  | Max absolute operand value                             | `1000000`                 |
| `CALCULATOR_DEFAULT_ENCODING` | File encoding                                          | `utf-8`                   |

Directories are created automatically on startup. Logging writes to
`CALCULATOR_LOG_FILE` (under `CALCULATOR_LOG_DIR` when relative).

## Usage

```bash
python main.py
# or
python -m app
```

### Supported commands

| Command                                                                                   | Description                           |
| ----------------------------------------------------------------------------------------- | ------------------------------------- |
| `add\|subtract\|multiply\|divide\|power\|root\|modulus\|int_divide\|percent\|abs_diff <n1> <n2>` | Perform a calculation                 |
| `history`                                                                               | Display calculation history           |
| `clear`                                                                                 | Clear calculation history             |
| `undo`                                                                                  | Undo the last calculation             |
| `redo`                                                                                  | Redo the last undone calculation      |
| `save`                                                                                  | Manually save history to CSV (pandas) |
| `load`                                                                                  | Load history from CSV (pandas)        |
| `help`                                                                                  | Show the dynamic help menu            |
| `exit`                                                                                  | Exit gracefully                       |

Example session:

```text
> add 10 5
Result: 15
> power 2 8
Result: 256
> percent 25 50
Result: 50.0
> undo
Undo successful.
> history
...
> save
History saved to history/calculation_history.csv
> exit
```

## Testing

```bash
pytest
pytest --cov=app --cov-report=term-missing --cov-fail-under=90
```

Target: **90%+** coverage on the `app` package (enforced locally and in CI).

## CI/CD (GitHub Actions)

Workflow: `.github/workflows/python-app.yml`

On every push or pull request to `main`, the pipeline:

1. Checks out the repository
2. Sets up Python 3.x
3. Installs dependencies from `requirements.txt`
4. Runs `pytest --cov=app --cov-fail-under=90`

The build **fails** if coverage drops below 90%.

## Design Patterns

| Pattern  | Implementation                                                 |
| -------- | -------------------------------------------------------------- |
| Factory  | `OperationFactory` in `app/operations.py`                     |
| Memento  | `CalculatorMemento` / `Caretaker` in `app/calculator_memento.py` |
| Observer | `LoggingObserver`, `AutoSaveObserver` in `app/calculator.py`   |
