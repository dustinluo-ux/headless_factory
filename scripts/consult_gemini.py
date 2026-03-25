#!/usr/bin/env python3
"""
consult_gemini.py — Send a query to Gemini with full project context.

Usage:
    python scripts/consult_gemini.py "Audit this valuation logic"
    python scripts/consult_gemini.py "What are the key risks?" --task 003
    python scripts/consult_gemini.py "Review SPEC.md scope" --model gemini-2.5-pro

Attaches:
    - identity.md Hard Limits → system prompt
    - repo_context.md + SPEC.md → user context block

Writes:
    agent_loop/result.md  (atomic)
    agent_loop/spend.log  (appended)

Requires:
    GEMINI_API_KEY in .env
"""

from __future__ import annotations

import argparse
import os
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _consult_base import (
    build_system_prompt,
    check_kill_switch,
    load_project_context,
    log_spend,
    write_result,
)

from google import genai
from google.genai import types


# ── Cost estimate (Gemini 2.0 Flash pricing as of 2025) ───────────────────────
# $0.075 / 1M input tokens, $0.30 / 1M output tokens
# Using conservative flat estimate: $0.002 per call for budget check
ESTIMATED_COST = Decimal("0.002")
DEFAULT_MODEL = "gemini-2.0-flash"
PROVIDER = "gemini"


def call_gemini(
    query: str,
    model: str,
    task_id: str,
) -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[FATAL] GEMINI_API_KEY not set in .env", file=sys.stderr)
        sys.exit(1)

    check_kill_switch(ESTIMATED_COST)

    context = load_project_context()
    system_prompt = build_system_prompt()

    user_message = f"""## Project Context

{context}

---

## Query

{query}"""

    print(f"  Calling {model}...")
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model=model,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.2,      # Low temp — precision over creativity
            max_output_tokens=4096,
        ),
    )

    response_text = response.text
    usage = response.usage_metadata
    total_tokens = (usage.prompt_token_count or 0) + (usage.candidates_token_count or 0)

    # Actual cost calculation (Gemini 2.0 Flash: $0.075/1M input, $0.30/1M output)
    input_cost = Decimal(str(usage.prompt_token_count or 0)) * Decimal("0.000000075")
    output_cost = Decimal(str(usage.candidates_token_count or 0)) * Decimal("0.0000003")
    actual_cost = input_cost + output_cost

    log_spend(PROVIDER, model, actual_cost, total_tokens)
    write_result(
        provider=PROVIDER,
        model=model,
        query=query,
        response=response_text,
        task_id=task_id,
        cost_usd=actual_cost,
        tokens=total_tokens,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Consult Gemini with project context → agent_loop/result.md"
    )
    parser.add_argument("query", help="Question or instruction to send to Gemini")
    parser.add_argument("--task", default="—", help="Task ID to tag this result with")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Gemini model (default: {DEFAULT_MODEL})")
    args = parser.parse_args()

    print(f"\nGemini Consult")
    print(f"  Model : {args.model}")
    print(f"  Task  : {args.task}")
    print(f"  Query : {args.query[:80]}{'...' if len(args.query) > 80 else ''}\n")

    try:
        call_gemini(args.query, args.model, args.task)
    except RuntimeError as e:
        print(f"\n[FATAL] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
