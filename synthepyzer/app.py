"""Synthepyzer desktop entry point."""

from __future__ import annotations


def main() -> int:
    try:
        from .main_window import run
    except ModuleNotFoundError as exc:  # pragma: no cover - depends on desktop package
        if exc.name and exc.name.startswith("PyQt6"):
            print("PyQt6 is not installed. Install the UI extra with: python3 -m pip install -e '.[ui]'")
            return 1
        raise
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
