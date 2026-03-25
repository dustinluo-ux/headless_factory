# PORTFOLIO.md — Multi-Project Index

> This file lives in the Headless Factory root.
> It is the Lab Director's entry point for cross-project oversight.
> Update it manually when you bootstrap, archive, or kill a project.

---

## Active Projects

| Project | Path | Status | Purpose | Budget Used | Last Audit |
|---------|------|--------|---------|-------------|------------|
| *(none yet)* | | | | | |

**Status values**: `ACTIVE` · `MAINTENANCE` · `ARCHIVED` · `KILLED`

To populate automatically: `python scripts/portfolio_report.py --paths [path1] [path2] ...`

---

## The Lab Director Pattern

The Headless Factory can act as its own **Lab Director** — a meta-project that monitors
all active child projects and allocates attention without starting a new repo.

### When to use this pattern

- You have 3+ active headless projects running simultaneously
- You want a single Claude Code session to triage across them
- You need a weekly roll-up of spend, status, and blockers

### How to run a Lab Director session

Open the Headless Factory repo in Claude Code and say:

```
"Act as Lab Director. Read PORTFOLIO.md and scan each active project's
CONTEXT.md, loop_state.md, and spend.log. Report status, flag blockers,
and recommend where attention is needed most."
```

Claude will:
1. Read `PORTFOLIO.md` (this file) for the project list
2. For each active project, read `[path]/agent_loop/loop_state.md` + `[path]/CONTEXT.md`
3. Read `[path]/agent_loop/spend.log` for spend totals
4. Output a prioritised status table with recommended next actions

### Automated roll-up (no LLM needed)

For a fast, cheap status check without API spend:

```bash
python scripts/portfolio_report.py \
  --paths ../project-a ../project-b ../project-c \
  --output portfolio_status.md
```

Emits `portfolio_status.md` — a structured markdown summary ready to paste into a
Lab Director session as context.

---

## Attention Allocation Rules

When running a Lab Director session, Claude prioritises projects using this order:

1. **BLOCKED** — any project where `loop_state.md` has a non-empty "Blocked by" field
2. **Budget warning** — any project where cumulative spend > 80% of `BUDGET_USD`
3. **Stale** — any project with no `loop_state.md` update in > 7 days
4. **Lifecycle drift** — any project where `SPEC.md` lifecycle status is inconsistent with
   observed activity (e.g. `MAINTENANCE` but active commits)
5. **Active build** — all other `ACTIVE` projects, ranked by milestone proximity

---

## Adding a Project to the Portfolio

After bootstrapping a new project, add a row to the Active Projects table above:

```
| my-project | C:/path/to/my-project | ACTIVE | One-sentence purpose | $0.00 | YYYY-MM-DD |
```

The `portfolio_report.py` script will keep spend and status current automatically.

---

## Lifecycle Transitions

| Transition | Trigger | Action required |
|-----------|---------|----------------|
| `ACTIVE` → `MAINTENANCE` | All acceptance criteria met; no new features planned | Update `SPEC.md` status field; reduce `BUDGET_USD` to maintenance level |
| `MAINTENANCE` → `ARCHIVED` | No changes in 30 days; project is stable reference | Move path to "Archived" section below; keep repo intact |
| `ACTIVE` → `KILLED` | Kill conditions in `SPEC.md` met; ROI negative | Run Auditor to confirm; update `SPEC.md`; close GitHub repo or make private |
| `ARCHIVED` → `ACTIVE` | Revival decision made | Re-bootstrap or update `SPEC.md` scope; reset `BUDGET_USD` |

---

## Archived Projects

| Project | Path | Archived Date | Reason |
|---------|------|--------------|--------|
| *(none yet)* | | | |

---

## Killed Projects

| Project | Killed Date | Kill Reason |
|---------|------------|-------------|
| *(none yet)* | | |
