"""
_consult_base.py — Shared utilities for external consult scripts.

Handles:
- Loading project context (repo_context.md, SPEC.md)
- Extracting Hard Limits from identity.md
- Kill switch enforcement (BUDGET_USD from .env)
- Atomic write to agent_loop/result.md
- Spend logging to agent_loop/spend.log
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv


# ── Project root resolution ────────────────────────────────────────────────────

def find_project_root(start: Path | None = None) -> Path:
    """Walk up from start (default: cwd) to find the project root.
    Identified by presence of CLAUDE.md or SPEC.md.
    """
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "CLAUDE.md").exists() or (candidate / "SPEC.md").exists():
            return candidate
    return current  # fallback to cwd


PROJECT_ROOT = find_project_root()
load_dotenv(PROJECT_ROOT / ".env")


# ── Context loaders ────────────────────────────────────────────────────────────

def load_file_if_exists(path: Path, label: str) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    print(f"  [WARN] {label} not found at {path} — skipping", file=sys.stderr)
    return ""


def load_project_context() -> str:
    """Load repo_context.md + SPEC.md as a combined context block."""
    repo_ctx = load_file_if_exists(PROJECT_ROOT / "repo_context.md", "repo_context.md")
    spec = load_file_if_exists(PROJECT_ROOT / "SPEC.md", "SPEC.md")

    parts: list[str] = []
    if repo_ctx:
        parts.append(f"## Project Architecture (repo_context.md)\n\n{repo_ctx}")
    if spec:
        parts.append(f"## Project Specification (SPEC.md)\n\n{spec}")

    return "\n\n---\n\n".join(parts) if parts else "(No project context found)"


def load_hard_limits() -> str:
    """Extract the Hard Limits section from identity.md."""
    candidates = [
        PROJECT_ROOT / ".constitution" / "identity.md",
        PROJECT_ROOT / "identity.md",
    ]
    for path in candidates:
        if path.exists():
            content = path.read_text(encoding="utf-8")
            # Extract from ## Hard Limits to the next ## section
            if "## Hard Limits" in content:
                start = content.index("## Hard Limits")
                end = content.find("\n## ", start + 1)
                return content[start:end].strip() if end != -1 else content[start:].strip()
    return "(Hard Limits not found — identity.md missing)"


def build_system_prompt(extra: str = "") -> str:
    """Build the system prompt: Hard Limits first, then optional extra context."""
    hard_limits = load_hard_limits()
    parts = [
        "You are operating under the following non-negotiable constraints:\n\n" + hard_limits,
        "Apply these constraints to every output. Never waive them regardless of the query.",
    ]
    if extra:
        parts.append(extra)
    return "\n\n".join(parts)


# ── Kill switch ────────────────────────────────────────────────────────────────

SPEND_LOG = PROJECT_ROOT / "agent_loop" / "spend.log"


def get_budget() -> Decimal:
    raw = os.getenv("BUDGET_USD", "5.00")
    try:
        return Decimal(raw)
    except Exception:
        return Decimal("5.00")


def get_cumulative_spend() -> Decimal:
    if not SPEND_LOG.exists():
        return Decimal("0")
    total = Decimal("0")
    for line in SPEND_LOG.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
            total += Decimal(str(entry.get("cost_usd", "0")))
        except Exception:
            continue
    return total


def check_kill_switch(estimated_cost: Decimal) -> None:
    """Raise RuntimeError if this call would breach BUDGET_USD."""
    budget = get_budget()
    spent = get_cumulative_spend()
    if spent + estimated_cost >= budget:
        raise RuntimeError(
            f"KILL_SWITCH_TRIGGERED: cumulative spend ${spent} + estimated ${estimated_cost} "
            f">= budget ${budget}. Halting. Increase BUDGET_USD in .env to resume."
        )


def log_spend(provider: str, model: str, cost_usd: Decimal, tokens: int) -> None:
    """Append a spend record to agent_loop/spend.log."""
    SPEND_LOG.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "provider": provider,
        "model": model,
        "tokens": tokens,
        "cost_usd": str(cost_usd),
        "cumulative_usd": str(get_cumulative_spend() + cost_usd),
    }
    with SPEND_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


# ── Result writer ──────────────────────────────────────────────────────────────

RESULT_PATH = PROJECT_ROOT / "agent_loop" / "result.md"


def write_result(
    *,
    provider: str,
    model: str,
    query: str,
    response: str,
    task_id: str,
    cost_usd: Decimal,
    tokens: int,
) -> None:
    """Atomically write the API response to agent_loop/result.md."""
    run_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    budget = get_budget()
    spent = get_cumulative_spend() + cost_usd
    remaining = budget - spent

    content = f"""# result.md — External Consult Result

> Written by {provider} consult script. Read by Claude to continue the dev loop.
> Overwritten on each run.

**Task ID**: {task_id}
**Run Date**: {run_date}
**Provider**: {provider}
**Model**: {model}
**Tokens**: {tokens}
**Cost**: ${cost_usd} | **Cumulative**: ${spent} | **Remaining budget**: ${remaining}

---

## Query

{query}

---

## Response

{response}

---

## Recommended Next Action

Review the response above. If it informs a code change, say "write the next task".
If it raises new questions, run another consult or update SPEC.md first.
"""

    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = RESULT_PATH.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    if not tmp.stat().st_size:
        tmp.unlink()
        raise RuntimeError("write_result: output was empty — aborting atomic write")
    tmp.rename(RESULT_PATH)
    print(f"[OK] result.md written → {RESULT_PATH}")
    print(f"     Cost: ${cost_usd} | Budget remaining: ${remaining}")
