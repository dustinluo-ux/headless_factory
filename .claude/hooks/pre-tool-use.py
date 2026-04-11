#!/usr/bin/env python3
"""
Pre-tool-use hook: BUDGET_USD Kill Switch
Deploy to: headless-factory/.claude/hooks/pre-tool-use.py

Claude Code calls this before every tool use.
Input (stdin): JSON with tool name and input
Output: exit 0 = allow, exit 2 = block with message
"""

import json
import os
import sys
from decimal import Decimal, InvalidOperation

BUDGET_ENV = "BUDGET_USD"
COST_LOG = ".claude/hooks/.cost_accumulator"


def get_budget() -> Decimal | None:
    raw = os.environ.get(BUDGET_ENV)
    if not raw:
        return None
    try:
        return Decimal(raw)
    except InvalidOperation:
        return None


def get_accumulated_cost() -> Decimal:
    try:
        with open(COST_LOG) as f:
            return Decimal(f.read().strip())
    except (FileNotFoundError, InvalidOperation):
        return Decimal("0")


def main() -> None:
    budget = get_budget()
    if budget is None:
        # No budget set — allow all tool use
        sys.exit(0)

    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        # Can't parse input — allow (fail open)
        sys.exit(0)

    tool_name = hook_input.get("tool_name", "unknown")
    accumulated = get_accumulated_cost()

    if accumulated >= budget:
        msg = (
            f"KILL SWITCH: BUDGET_USD=${budget} exceeded "
            f"(accumulated=${accumulated:.4f}). "
            f"Blocking tool: {tool_name}. "
            f"Unset {BUDGET_ENV} or increase budget to continue."
        )
        print(json.dumps({"decision": "block", "reason": msg}))
        sys.exit(2)

    # Allow — log that we checked
    sys.exit(0)


if __name__ == "__main__":
    main()
