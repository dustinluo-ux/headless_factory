# MASTER_RULES.md — Universal Constitution

> Applies to every project bootstrapped by this toolkit, regardless of language or domain.
> Governs orchestration, security, and code quality only.
> Domain expertise lives in `identity.md`. Domain procedures live in `skills/`.

---

## § 1 — Orchestration

### 1.1 Plan Before Act

No file may be written, no API may be called, no external state may be mutated without a passing
plan. A plan is a `project_plan.md` at the project root containing ALL of these sections —
a plan missing any section is invalid and must not be executed:

| Required Section | Purpose |
|-----------------|---------|
| `## Objective` | One sentence: what this plan accomplishes |
| `## Files Changed` | Explicit list of every file that will be created or modified |
| `## Single Point of Failure` | Pre-mortem: the one thing most likely to make this plan fail |
| `## Rollback` | How to restore prior state if execution fails mid-way |
| `## Acceptance` | How to verify the plan succeeded |

The **Single Point of Failure** section must be substantive — not a placeholder.
"TBD", "Unknown", "N/A" are not acceptable entries.

### 1.2 Deterministic Execution

- All randomness must be seeded and documented.
- All branching logic must be explicit — no silent fallbacks.
- Pipelines must be idempotent: running twice produces the same result as running once.

### 1.3 Atomic Writes

- Write to a `.tmp` file, validate non-empty, then rename to target.
- Never write directly to a production file.
- If any step in a pipeline fails, halt and surface the error. Do not proceed.

---

## § 2 — Security

### 2.1 Kill Switch — API Spend

Every agent session that calls an external API must:
1. Load a spend budget from `.env` (`BUDGET_USD`).
2. Track cumulative spend in session state.
3. Halt and log a `KILL_SWITCH_TRIGGERED` event when spend exceeds `BUDGET_USD`.
4. Never resume without explicit user confirmation.

Default if unset: **$5.00 USD**.

### 2.2 Secrets Management

- Secrets are loaded from `.env` only. Never hardcode credentials anywhere.
- `.env` must be in `.gitignore`. Verify before every commit.
- Log file names and keys — never log values.

### 2.3 Scope Containment

- The agent may only write within the project root unless explicitly granted elevated scope.
- Network calls are permitted only to domains listed in `SPEC.md § Allowed Domains`.

---

## § 3 — Code Quality

These principles apply regardless of programming language:

- **Type safety**: Use types where the language supports them.
- **No bare error suppression**: Every caught exception must be logged or re-raised.
- **Structured logging**: JSON-lines preferred. Level controlled by `LOG_LEVEL` env var.
- **No hardcoded configuration**: All config via environment variables or explicit config files.
- **Monetary values**: Never use floating point for money. Use fixed-point, decimal, or integer types.

---

## § 4 — The 4-File Protocol

Every project must contain these four files before any work begins:

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Agent instructions — persona, constraints, tool permissions for this project |
| `SPEC.md` | Source of truth — requirements, data sources, allowed domains, acceptance criteria |
| `CONTEXT.md` | State log — current status, last action, open decisions, blockers |
| `SKILL.md` | Procedures — reusable techniques and patterns for this project's domain |

These files are initialized at bootstrap and updated (never replaced wholesale) during the project lifecycle.

---

## § 5 — Amendment Protocol

This constitution may be amended only by editing `MASTER_RULES.md` directly in the toolkit repo
and committing with the prefix `[CONSTITUTION]`. Active projects should have their
`.constitution/MASTER_RULES.md` updated manually after any amendment.
