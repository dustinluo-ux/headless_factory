#!/usr/bin/env python3
"""
consult_market.py — Live market intelligence via Perplexity Sonar on OpenRouter.

Usage:
    python scripts/consult_market.py "Current DCF discount rates for Asian infrastructure"
    python scripts/consult_market.py "Tokenised real estate liquidity risks 2025" --task 004
    python scripts/consult_market.py "AAPL valuation consensus" --model perplexity/sonar-pro

Attaches:
    - identity.md Hard Limits → system prompt
    - repo_context.md + SPEC.md → user context block

Writes:
    agent_loop/result.md  (atomic)
    agent_loop/spend.log  (appended)

Requires:
    OPENROUTER_API_KEY in .env
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
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


# ── Pricing (Perplexity sonar-pro via OpenRouter, ~2025) ──────────────────────
# $3.00 / 1M tokens + $5.00 / 1000 requests
# Conservative per-call estimate for budget gate: $0.01
ESTIMATED_COST = Decimal("0.01")
DEFAULT_MODEL = "perplexity/sonar-pro"
PROVIDER = "openrouter/perplexity"
OPENROUTER_BASE = "https://openrouter.ai/api/v1/chat/completions"


def call_openrouter(
    query: str,
    model: str,
    task_id: str,
) -> None:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("[FATAL] OPENROUTER_API_KEY not set in .env", file=sys.stderr)
        sys.exit(1)

    check_kill_switch(ESTIMATED_COST)

    context = load_project_context()
    system_prompt = build_system_prompt()

    user_message = f"""## Project Context

{context}

---

## Query

{query}"""

    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.2,
        "max_tokens": 4096,
    }).encode("utf-8")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/headless-factory",
        "X-Title": "Headless Factory — Market Consult",
    }

    print(f"  Calling {model} via OpenRouter...")
    req = urllib.request.Request(OPENROUTER_BASE, data=payload, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"[FATAL] HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)

    response_text = data["choices"][0]["message"]["content"]

    # Extract citations if Perplexity returns them
    citations = data.get("citations", [])
    if citations:
        citation_block = "\n\n---\n\n## Sources\n\n" + "\n".join(
            f"- {c}" for c in citations
        )
        response_text += citation_block

    usage = data.get("usage", {})
    total_tokens = usage.get("total_tokens", 0)

    # Actual cost: $3/1M tokens + $5/1000 requests
    token_cost = Decimal(str(total_tokens)) * Decimal("0.000003")
    request_cost = Decimal("0.005")
    actual_cost = token_cost + request_cost

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
        description="Live market intelligence via Perplexity Sonar → agent_loop/result.md"
    )
    parser.add_argument("query", help="Market intelligence question")
    parser.add_argument("--task", default="—", help="Task ID to tag this result with")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model (default: {DEFAULT_MODEL})")
    args = parser.parse_args()

    print(f"\nMarket Consult (Perplexity via OpenRouter)")
    print(f"  Model : {args.model}")
    print(f"  Task  : {args.task}")
    print(f"  Query : {args.query[:80]}{'...' if len(args.query) > 80 else ''}\n")

    try:
        call_openrouter(args.query, args.model, args.task)
    except RuntimeError as e:
        print(f"\n[FATAL] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
