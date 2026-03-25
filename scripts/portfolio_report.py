"""
portfolio_report.py — Cross-project portfolio status report.

Walks a list of project directories, reads each project's:
  - CONTEXT.md (lifecycle status, last audit)
  - agent_loop/loop_state.md (current objective, last task, blockers)
  - agent_loop/spend.log (cumulative spend vs budget)
  - .env (BUDGET_USD)

Emits a structured markdown summary suitable for Lab Director review or
pasting into a Claude Code session as context.

Usage:
    python scripts/portfolio_report.py --paths ../proj-a ../proj-b
    python scripts/portfolio_report.py --paths ../proj-a ../proj-b --output portfolio_status.md
    python scripts/portfolio_report.py --from-portfolio  # reads paths from PORTFOLIO.md

Options:
    --paths PATH [PATH ...]   Project directories to scan
    --from-portfolio          Parse paths from PORTFOLIO.md in the factory root
    --output FILE             Write report to file (default: print to stdout)
    --factory ROOT            Path to the factory repo (default: cwd)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path


# ── Readers ────────────────────────────────────────────────────────────────────

def read_file(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def extract_field(text: str, label: str) -> str:
    """Extract a value from '**Label**: value' or '| Label | value |' patterns."""
    # Bold label pattern
    m = re.search(rf"\*\*{re.escape(label)}\*\*[:\s]+`?([^\n`|]+)`?", text)
    if m:
        return m.group(1).strip()
    # Table cell pattern
    m = re.search(rf"\|\s*{re.escape(label)}\s*\|\s*`?([^|\n`]+)`?\s*\|", text)
    if m:
        return m.group(1).strip()
    return ""


def get_lifecycle_status(project_path: Path) -> str:
    context = read_file(project_path / "CONTEXT.md")
    spec = read_file(project_path / "SPEC.md")
    status = extract_field(context, "Lifecycle Status")
    if not status:
        status = extract_field(spec, "Status")
    return status or "UNKNOWN"


def get_last_audit(project_path: Path) -> str:
    context = read_file(project_path / "CONTEXT.md")
    spec = read_file(project_path / "SPEC.md")
    audit = extract_field(context, "Last Audit")
    if not audit:
        audit = extract_field(spec, "Last Audit")
    return audit or "—"


def get_current_objective(project_path: Path) -> str:
    loop_state = read_file(project_path / "agent_loop" / "loop_state.md")
    m = re.search(r"## Current Objective\s*\n+(.*?)(?=\n---|\n##|\Z)", loop_state, re.DOTALL)
    if m:
        obj = m.group(1).strip()
        obj = re.sub(r"^\*|\*$|^\(|\)$", "", obj).strip()
        return obj[:120] + "..." if len(obj) > 120 else obj
    return "—"


def get_blockers(project_path: Path) -> str:
    loop_state = read_file(project_path / "agent_loop" / "loop_state.md")
    m = re.search(r"\*\*Blocked by\*\*:\s*(.+)", loop_state)
    if m:
        val = m.group(1).strip()
        return val if val.lower() not in ("none", "*(none)*", "") else "—"
    return "—"


def get_last_task_status(project_path: Path) -> str:
    loop_state = read_file(project_path / "agent_loop" / "loop_state.md")
    m = re.search(r"\*\*Status\*\*:\s*(.+)", loop_state)
    return m.group(1).strip() if m else "—"


def get_spend(project_path: Path) -> tuple[Decimal, Decimal]:
    """Return (cumulative_spend, budget) from spend.log and .env."""
    spend_log = project_path / "agent_loop" / "spend.log"
    env_file = project_path / ".env"

    # Budget from .env
    budget = Decimal("5.00")
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            m = re.match(r"BUDGET_USD\s*=\s*([0-9.]+)", line.strip())
            if m:
                try:
                    budget = Decimal(m.group(1))
                except InvalidOperation:
                    pass

    # Cumulative spend from spend.log
    total = Decimal("0")
    if spend_log.exists():
        for line in spend_log.read_text(encoding="utf-8").splitlines():
            try:
                entry = json.loads(line)
                total += Decimal(str(entry.get("cost_usd", "0")))
            except Exception:
                continue

    return total, budget


def days_since_modified(path: Path) -> int | None:
    """Days since file was last modified."""
    if not path.exists():
        return None
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    delta = datetime.now(timezone.utc) - mtime
    return delta.days


# ── Portfolio.md parser ────────────────────────────────────────────────────────

def parse_portfolio_paths(factory_root: Path) -> list[Path]:
    """Extract project paths from PORTFOLIO.md Active Projects table."""
    portfolio = factory_root / "PORTFOLIO.md"
    if not portfolio.exists():
        sys.exit(f"ERROR: PORTFOLIO.md not found at {portfolio}")

    paths: list[Path] = []
    in_active_table = False

    for line in portfolio.read_text(encoding="utf-8").splitlines():
        if "## Active Projects" in line:
            in_active_table = True
            continue
        if in_active_table and line.startswith("## "):
            break  # hit next section
        if in_active_table and line.startswith("|") and "none yet" not in line.lower():
            cells = [c.strip() for c in line.split("|")]
            # Table: | Project | Path | Status | ...
            if len(cells) >= 4 and cells[2] and not cells[2].startswith("---"):
                raw_path = cells[2]
                if raw_path and raw_path not in ("Path", ""):
                    p = Path(raw_path)
                    if not p.is_absolute():
                        p = factory_root / p
                    paths.append(p)

    return paths


# ── Report builder ─────────────────────────────────────────────────────────────

def attention_priority(status: str, spend: Decimal, budget: Decimal,
                       blockers: str, days_stale: int | None) -> int:
    """Lower number = higher priority."""
    if blockers not in ("—", ""):
        return 1
    if budget > 0 and spend / budget > Decimal("0.8"):
        return 2
    if days_stale is not None and days_stale > 7:
        return 3
    if status not in ("ACTIVE",):
        return 4
    return 5


def build_report(project_paths: list[Path], factory_root: Path) -> str:
    run_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rows: list[dict] = []

    for p in project_paths:
        if not p.exists():
            rows.append({"name": p.name, "path": str(p), "error": "PATH NOT FOUND"})
            continue

        name = p.name
        status = get_lifecycle_status(p)
        last_audit = get_last_audit(p)
        objective = get_current_objective(p)
        blockers = get_blockers(p)
        last_task_status = get_last_task_status(p)
        spend, budget = get_spend(p)
        pct = int(spend / budget * 100) if budget > 0 else 0
        loop_state_path = p / "agent_loop" / "loop_state.md"
        days_stale = days_since_modified(loop_state_path)
        priority = attention_priority(status, spend, budget, blockers, days_stale)

        rows.append({
            "name": name,
            "path": str(p),
            "status": status,
            "last_audit": last_audit,
            "objective": objective,
            "blockers": blockers,
            "last_task_status": last_task_status,
            "spend": spend,
            "budget": budget,
            "pct": pct,
            "days_stale": days_stale,
            "priority": priority,
            "error": None,
        })

    rows.sort(key=lambda r: r.get("priority", 99))

    lines: list[str] = [
        "# Portfolio Status Report",
        "",
        f"> Generated: {run_ts}",
        f"> Projects scanned: {len(project_paths)}",
        "",
        "---",
        "",
        "## Summary Table",
        "",
        "| Priority | Project | Status | Spend | Stale | Blockers | Last Task |",
        "|----------|---------|--------|-------|-------|----------|-----------|",
    ]

    for r in rows:
        if r.get("error"):
            lines.append(f"| — | {r['name']} | ❌ {r['error']} | — | — | — | — |")
            continue
        stale_str = f"{r['days_stale']}d" if r["days_stale"] is not None else "—"
        pct_str = f"${r['spend']} / ${r['budget']} ({r['pct']}%)"
        flag = "🔴" if r["priority"] <= 2 else ("🟡" if r["priority"] == 3 else "🟢")
        lines.append(
            f"| {flag} {r['priority']} | **{r['name']}** | `{r['status']}` | "
            f"{pct_str} | {stale_str} | {r['blockers'][:40]} | {r['last_task_status']} |"
        )

    lines += ["", "---", "", "## Project Details", ""]

    for r in rows:
        if r.get("error"):
            lines += [f"### ❌ {r['name']}", "", f"**Error**: {r['error']}", ""]
            continue
        lines += [
            f"### {r['name']}",
            "",
            f"**Path**: `{r['path']}`  ",
            f"**Status**: `{r['status']}` · **Last Audit**: {r['last_audit']}  ",
            f"**Spend**: ${r['spend']} of ${r['budget']} ({r['pct']}%)  ",
            f"**Days since loop_state update**: {r['days_stale'] if r['days_stale'] is not None else '—'}",
            "",
            f"**Current Objective**: {r['objective']}",
            "",
            f"**Blockers**: {r['blockers']}",
            "",
            "---",
            "",
        ]

    lines += [
        "## Lab Director Recommended Actions",
        "",
        "*(Review the 🔴 priority items above and address in order.)*",
        "*(Paste this report into a Claude Code session and say: \"Act as Lab Director and issue tasks.\")*",
        "",
    ]

    return "\n".join(lines)


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Portfolio status report")
    parser.add_argument("--paths", nargs="+", help="Project directories to scan")
    parser.add_argument(
        "--from-portfolio",
        action="store_true",
        help="Parse project paths from PORTFOLIO.md",
    )
    parser.add_argument("--output", help="Write report to this file (default: stdout)")
    parser.add_argument(
        "--factory",
        default=".",
        help="Path to the factory repo root (default: cwd)",
    )
    args = parser.parse_args()

    factory_root = Path(args.factory).resolve()

    if args.from_portfolio:
        project_paths = parse_portfolio_paths(factory_root)
        if not project_paths:
            sys.exit("No active projects found in PORTFOLIO.md")
    elif args.paths:
        project_paths = [Path(p).resolve() for p in args.paths]
    else:
        parser.print_help()
        sys.exit(1)

    report = build_report(project_paths, factory_root)

    if args.output:
        out = Path(args.output)
        out.write_text(report, encoding="utf-8")
        print(f"[OK] Report written → {out}")
    else:
        print(report)


if __name__ == "__main__":
    main()
