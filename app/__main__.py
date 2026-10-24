"""Entry point for running the calculator as a module (python -m app)."""

from app.repl import run_repl


def main() -> None:  # pragma: no cover
    run_repl()


if __name__ == "__main__":  # pragma: no cover
    main()
