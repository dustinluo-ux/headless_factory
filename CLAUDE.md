# Headless Factory — Context Card

Bootstrap toolkit: spins up AI-assisted projects with consistent structure,
governance, and guardrails. Claude Code executes bootstraps on demand.

## Bootstrap

**Trigger phrases**: "init a project", "bootstrap", "create a new project",
"start a new repo", "spin up [name]", "new project called [name]"

Collect 6 fields (ask all missing required ones in one message):
`name` (req), `purpose` (req), `target_dir` (req), `github` (req: private/public/none),
`skills` (opt, e.g. `valuation`), `budget` (opt, default `5.00`)

Full 8-step procedure: `.claude/commands/bootstrap-procedure.md`

## Dev Loop (in every bootstrapped project)

SessionStart Autopilot in each project's CLAUDE.md:
load CONTEXT.md + loop_state.md → SPEC incomplete? → fill via gstack →
Auditor gate (5 Hard Limits) → write task.md → Cursor implements →
run consult script → Claude reads result.md → update CONTEXT → repeat.

## Consult Scripts (copied into every bootstrapped project)

| Script | Purpose | Key env var |
|--------|---------|-------------|
| `consult_gemini.py "q" --task N` | Analytical queries, code audit | `GEMINI_API_KEY` |
| `consult_market.py "q" --task N` | Live market data (Perplexity Sonar) | `OPENROUTER_API_KEY` |
| `run_r_and_d.py [pod] --task N` | Structured R&D research | `GEMINI_API_KEY` |
| `summarize_run.py --task N` | Format stdout → result.md (pipe target) | — |

## Portfolio

`PORTFOLIO.md` — one row per project. Update at bootstrap/archive/kill.
`python scripts/portfolio_report.py --from-portfolio` or `/lab-director`

## Agent Layer

**Skills**: `write_task`, `build_feature`, `refactor_safe`, `repo_map`,
`test_generator`, `bug_hunt` — all in `agent/skills/`.
**Teams**: Researcher (external facts → `research/`) + Auditor (5 Hard Limits gate).
**gstack** (if installed): `/office-hours` → `/plan-ceo-review` → `/plan-eng-review` → `/retro`
**Skill packs** (opt-in at bootstrap): `valuation` adds DCF/NAV templates + Decimal arithmetic.

## Key Paths

```
headless_factory/
├── templates/       ← rendered into every bootstrapped project
├── agent/           ← copied verbatim into every bootstrapped project
├── skills/          ← domain packs (valuation.md, ...)
├── scripts/         ← consult scripts + portfolio_report.py
├── .claude/
│   ├── commands/    ← bootstrap, bootstrap-procedure, lab-director, plan, risk
│   └── hooks/       ← pre-tool-use.py (kill switch) + post-tool-use.py (counter)
├── MASTER_RULES.md  ← universal constitution
├── identity.md      ← owner persona + Hard Limits
└── PORTFOLIO.md     ← active project index
```

## Hard Rules

1. Plan before act — no file writes without a passing plan in scope
2. Kill switch — BUDGET_USD enforced; halt on breach; never resume without confirmation
3. No float for money — Decimal only; hard failure
4. Secrets in .env only — never hardcode, never commit
5. Atomic writes — write to .tmp, validate non-empty, rename to target
6. No writes outside project root
7. No network to unlisted domains (each project's SPEC.md § Allowed Domains)

## DO NOT

- Commit `.env` or any secret
- Use `float` for monetary values
- Write code before planning and Auditor PASS
- Skip the Auditor gate before any irreversible action
- Overwrite bootstrapped project CLAUDE.md without reading it first
