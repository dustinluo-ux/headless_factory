"""
run_r_and_d.py — AutoResearch R&D Pod runner.

Reads a research/r_and_d_pod.md file, extracts the Query block, calls Gemini
with the questions as a structured research prompt, writes Findings back into
the pod file, and logs the run to agent_loop/result.md.

Usage:
    python scripts/run_r_and_d.py [pod_path] [--task ID]

    pod_path  Path to the R&D pod file (default: research/r_and_d_pod.md)
    --task    Task ID for spend log / result.md (default: "r&d")

Requires:
    GEMINI_API_KEY in .env
    google-genai >= 1.0.0  (uv add google-genai)
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

# Add scripts/ to path so _consult_base is importable when run from project root
sys.path.insert(0, str(Path(__file__).parent))
from _consult_base import (
    PROJECT_ROOT,
    build_system_prompt,
    check_kill_switch,
    load_project_context,
    log_spend,
    write_result,
)

try:
    from google import genai
    from google.genai import types as genai_types
except ImportError:
    sys.exit(
        "ERROR: google-genai not installed.\n"
        "Run: uv add google-genai  (or pip install google-genai)"
    )

import os

# ── Constants ──────────────────────────────────────────────────────────────────

DEFAULT_POD_PATH = PROJECT_ROOT / "research" / "r_and_d_pod.md"
MODEL = "gemini-2.0-flash"
# Gemini Flash pricing (per 1M tokens, as of 2025-03)
COST_PER_1K_INPUT = Decimal("0.000075")
COST_PER_1K_OUTPUT = Decimal("0.0003")


# ── Pod parser ─────────────────────────────────────────────────────────────────

def parse_pod(pod_text: str) -> dict[str, str]:
    """Extract topic, decision context, and questions from the Query block."""
    result: dict[str, str] = {"topic": "", "decision": "", "questions": ""}

    topic_m = re.search(r"\*\*Topic\*\*:\s*(.+)", pod_text)
    decision_m = re.search(r"\*\*Decision it supports\*\*:\s*(.+)", pod_text)
    if topic_m:
        result["topic"] = topic_m.group(1).strip()
    if decision_m:
        result["decision"] = decision_m.group(1).strip()

    # Extract numbered questions from the "Questions to answer" section
    q_section_m = re.search(
        r"### Questions to answer\s*(.*?)(?=\n---|\n##|\Z)", pod_text, re.DOTALL
    )
    if q_section_m:
        result["questions"] = q_section_m.group(1).strip()

    return result


def build_research_prompt(pod_data: dict[str, str], project_context: str) -> str:
    """Build the research query from parsed pod data."""
    topic = pod_data["topic"] or "(see questions below)"
    decision = pod_data["decision"] or "(not specified)"
    questions = pod_data["questions"] or "(no questions found in pod file)"

    return f"""You are a research analyst. Answer the following questions with precision.

**Research topic**: {topic}
**Decision this supports**: {decision}

**Questions to answer**:
{questions}

**Output format** — for each question:
- Restate the question as a heading
- Provide a concise, factual answer
- Cite the primary source (URL + retrieval date if web-sourced, or document name)
- Assign confidence: HIGH (primary source) / MEDIUM (secondary / aggregator) / LOW (inferred)
- Note any conflicts between sources

End with a 2–3 sentence synthesis covering: what was found, what remains uncertain,
and the single most important implication for the decision above.

Do not pad answers. Flag explicitly when a question cannot be answered with HIGH or MEDIUM confidence.

---

Project context (for relevance calibration):

{project_context}
"""


# ── Findings writer ────────────────────────────────────────────────────────────

def write_findings_to_pod(pod_path: Path, findings: str, model: str) -> None:
    """Atomically overwrite the Findings section of the pod file."""
    pod_text = pod_path.read_text(encoding="utf-8")
    run_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    new_findings = (
        f"## Findings\n\n"
        f"*Written by Researcher sub-agent. Do not edit manually.*\n\n"
        f"**Completed**: {run_ts}\n"
        f"**Model**: {model}\n\n"
        f"{findings}\n"
    )

    # Replace everything from "## Findings" to "## Action Required" (or end of file)
    pattern = r"(## Findings\s*\n)(.*?)(?=\n## Action Required|\Z)"
    replacement = new_findings + "\n"
    updated = re.sub(pattern, replacement, pod_text, flags=re.DOTALL)

    if updated == pod_text:
        # Section not found — append findings
        updated = pod_text.rstrip() + "\n\n" + new_findings

    tmp = pod_path.with_suffix(".tmp")
    tmp.write_text(updated, encoding="utf-8")
    if not tmp.stat().st_size:
        tmp.unlink()
        raise RuntimeError("write_findings_to_pod: output was empty — aborting")
    tmp.rename(pod_path)
    print(f"[OK] Findings written → {pod_path}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Run the R&D pod researcher")
    parser.add_argument(
        "pod_path",
        nargs="?",
        default=str(DEFAULT_POD_PATH),
        help="Path to r_and_d_pod.md (default: research/r_and_d_pod.md)",
    )
    parser.add_argument("--task", default="r&d", help="Task ID for spend log")
    parser.add_argument("--model", default=MODEL, help="Gemini model to use")
    args = parser.parse_args()

    pod_path = Path(args.pod_path)
    if not pod_path.is_absolute():
        pod_path = PROJECT_ROOT / pod_path
    if not pod_path.exists():
        sys.exit(f"ERROR: Pod file not found: {pod_path}\n"
                 f"Create it from: templates/research/r_and_d_pod.md.template")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        sys.exit("ERROR: GEMINI_API_KEY not set in .env")

    print(f"[run_r_and_d] Pod: {pod_path}")
    print(f"[run_r_and_d] Model: {args.model}")

    # Parse pod
    pod_text = pod_path.read_text(encoding="utf-8")
    pod_data = parse_pod(pod_text)
    if not pod_data["questions"]:
        sys.exit("ERROR: No questions found in pod file. Fill in '### Questions to answer' first.")

    # Build prompt
    project_context = load_project_context()
    query = build_research_prompt(pod_data, project_context)
    system_prompt = build_system_prompt()

    # Kill switch (estimate: ~4k tokens)
    estimated_cost = COST_PER_1K_INPUT * 4 + COST_PER_1K_OUTPUT * 2
    check_kill_switch(estimated_cost)

    # Call Gemini
    print("[run_r_and_d] Calling Gemini...")
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=args.model,
        contents=query,
        config=genai_types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.1,  # precision over creativity for research
        ),
    )

    findings = response.text or ""
    if not findings.strip():
        sys.exit("ERROR: Gemini returned empty response")

    # Costs
    usage = response.usage_metadata
    input_tokens = getattr(usage, "prompt_token_count", 0) or 0
    output_tokens = getattr(usage, "candidates_token_count", 0) or 0
    total_tokens = input_tokens + output_tokens
    cost = (
        COST_PER_1K_INPUT * Decimal(input_tokens) / 1000
        + COST_PER_1K_OUTPUT * Decimal(output_tokens) / 1000
    )

    log_spend("gemini", args.model, cost, total_tokens)

    # Write findings back to pod
    write_findings_to_pod(pod_path, findings, args.model)

    # Write result.md for Claude to read
    write_result(
        provider="Gemini (R&D Pod)",
        model=args.model,
        query=f"R&D Pod: {pod_data['topic'] or pod_path.name}",
        response=f"Findings written to `{pod_path.relative_to(PROJECT_ROOT)}`.\n\n"
                 f"**Synthesis excerpt**:\n\n{findings[-800:]}",
        task_id=args.task,
        cost_usd=cost,
        tokens=total_tokens,
    )


if __name__ == "__main__":
    main()
