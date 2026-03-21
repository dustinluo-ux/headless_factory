#!/usr/bin/env python3
"""
summarize_run.py — Format execution output into agent_loop/result.md

Usage:
    python scripts/summarize_run.py                    # reads stdin
    python scripts/summarize_run.py run.log            # reads log file
    python scripts/summarize_run.py run.log --task 3   # tag with task ID

The script:
  1. Reads raw execution output
  2. Extracts metrics matching patterns defined in .metrics_config (if present)
  3. Detects pass/fail from exit code or error patterns
  4. Writes agent_loop/result.md

Extend METRIC_PATTERNS for your project's output format.
"""

import re
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path


# ── Metric extraction patterns ────────────────────────────────────────────────
# Add patterns that match your script's stdout. Each entry:
#   name: label in result.md
#   pattern: regex with a named group 'val'
#   target: expected value (or None)
#
# Example: if your script prints "sharpe_ratio: 1.42", add:
#   {"name": "sharpe_ratio", "pattern": r"sharpe_ratio[:\s]+(?P<val>[\d.+-]+)", "target": "> 1.0"}

METRIC_PATTERNS: list[dict] = [
    # Default: capture any "key: value" lines that look like metrics
    # Override by editing this list for your project
]

ERROR_PATTERNS = [
    r"Error:",
    r"Traceback",
    r"FAILED",
    r"Exception:",
    r"KILL_SWITCH_TRIGGERED",
]

TAIL_LINES = 20


# ── Helpers ───────────────────────────────────────────────────────────────────

def read_input(source: str | None) -> str:
    if source and Path(source).exists():
        return Path(source).read_text(encoding="utf-8", errors="replace")
    return sys.stdin.read()


def extract_metrics(text: str) -> list[dict]:
    results = []
    for spec in METRIC_PATTERNS:
        m = re.search(spec["pattern"], text, re.IGNORECASE | re.MULTILINE)
        results.append({
            "name": spec["name"],
            "value": m.group("val") if m else "not found",
            "target": spec.get("target", "—"),
            "delta": "—",
        })
    return results


def detect_errors(text: str) -> list[str]:
    found = []
    for line in text.splitlines():
        if any(re.search(p, line) for p in ERROR_PATTERNS):
            found.append(line.strip())
    return found[:10]  # cap at 10 lines


def detect_status(text: str, errors: list[str]) -> str:
    if errors:
        if any("KILL_SWITCH" in e for e in errors):
            return "FAIL"
        return "PARTIAL"
    if re.search(r"\bFAILED\b|\bERROR\b", text, re.IGNORECASE):
        return "FAIL"
    return "PASS"


def tail(text: str, n: int = TAIL_LINES) -> str:
    lines = text.strip().splitlines()
    return "\n".join(lines[-n:]) if len(lines) > n else text.strip()


# ── Main ──────────────────────────────────────────────────────────────────────

def build_result_md(
    raw: str,
    task_id: str,
    script_name: str,
    run_date: str,
) -> str:
    metrics = extract_metrics(raw)
    errors = detect_errors(raw)
    status = detect_status(raw, errors)

    # Metrics table
    if metrics:
        header = "| Metric | Value | Target | Delta |\n|--------|-------|--------|-------|"
        rows = "\n".join(
            f"| {m['name']} | {m['value']} | {m['target']} | {m['delta']} |"
            for m in metrics
        )
        metrics_block = f"{header}\n{rows}"
    else:
        metrics_block = "*(No metric patterns configured — edit METRIC_PATTERNS in summarize_run.py)*"

    # Error block
    if errors:
        error_block = "```\n" + "\n".join(errors) + "\n```"
    else:
        error_block = "*(none)*"

    # Next action heuristic
    if status == "PASS":
        next_action = "All criteria passed. Write next task or close this objective."
    elif status == "PARTIAL":
        next_action = "Partial pass — review errors above before writing next task."
    else:
        next_action = "Run failed. Investigate errors before writing next task."

    return f"""# result.md — Run Result

> Written by summarize_run.py. Read by Claude.
> Claude reads ONLY this file to decide the next task. Do not read raw logs.
> Overwritten after each run.

**Task ID**: {task_id}
**Run Date**: {run_date}
**Script**: {script_name}
**Duration**: *(not measured — add `time` prefix to your run command if needed)*

---

## Outcome

**Status**: {status}
**One-line summary**: *(fill in manually if auto-detection is insufficient)*

---

## Key Metrics

{metrics_block}

---

## Errors / Warnings

{error_block}

---

## Raw Output Tail

```
{tail(raw)}
```

---

## Recommended Next Action

{next_action}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize a run into agent_loop/result.md")
    parser.add_argument("source", nargs="?", help="Log file path (default: stdin)")
    parser.add_argument("--task", default="—", help="Task ID to tag this result with")
    parser.add_argument("--script", default="unknown", help="Name of the script that was run")
    parser.add_argument("--out", default="agent_loop/result.md", help="Output path")
    args = parser.parse_args()

    raw = read_input(args.source)
    run_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    script_name = args.source or args.script

    content = build_result_md(
        raw=raw,
        task_id=args.task,
        script_name=script_name,
        run_date=run_date,
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.rename(out_path)

    print(f"[OK] result.md written → {out_path}")
    print(f"     Status: {content.split('**Status**: ')[1].split()[0]}")


if __name__ == "__main__":
    main()
