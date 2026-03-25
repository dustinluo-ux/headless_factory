"""
Headless Factory — entry point.

Usage:
    uv run main.py report [--paths PATH ...] [--from-portfolio] [--output FILE]
    uv run main.py report --help

Delegates to scripts/portfolio_report.py for cross-project status roll-up.
For consult scripts, run them directly:
    python scripts/consult_gemini.py "query" --task N
    python scripts/consult_market.py "query" --task N
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scripts"))


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] != "report":
        print(__doc__)
        sys.exit(0)

    # Delegate to portfolio_report.py with remaining args
    sys.argv = [sys.argv[0]] + sys.argv[2:]
    from portfolio_report import main as report_main
    report_main()


if __name__ == "__main__":
    main()
