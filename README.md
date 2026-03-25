# Headless Factory — Project Bootstrap Toolkit

A one-repo system for spinning up new AI-assisted projects with consistent structure,
governance, and guardrails. Designed for Claude Code + Cursor workflows.

**No CLI. No setup. Open this repo in Claude Code and say "bootstrap a new project."**

---

## What it does

Every bootstrapped project gets:

- A **4-file governance protocol** stamped into the root
- The **Universal Constitution** (orchestration rules, security spines) injected as read-only
- The **owner's identity/persona** available as a reference file
- A **uv-managed Python environment** with testing and linting pre-configured
- A **kill switch** for API spend baked into `.env`
- Optional **domain skill packs** appended on request (e.g. `valuation`)
- **External consult scripts** for querying Gemini and Perplexity with project context
- **Agent Teams** — Researcher and Auditor sub-agent roles wired into every CLAUDE.md
- **Planning skill hooks** — gstack `/office-hours`, `/plan-ceo-review`, `/plan-eng-review`, `/retro` mapped to project phases
- **SessionStart Autopilot** — every session self-starts: loads state, runs planning cascade, gates on Auditor, writes first task — no manual prompting required

---

## How to bootstrap

Open this repo in Claude Code and say any of:

```
"bootstrap a new project"
"init a project called <name>"
"spin up <name>"
"new project called <name>"
```

Claude will ask for: **name**, **purpose**, **target directory**, and **GitHub visibility**
(private / public / none) — then execute the full procedure without further prompting.

### After bootstrap — immediate SOP

| Step | Who | Action |
|------|-----|--------|
| 1 | You | Open the new project in Claude Code |
| 2 | You | Fill `.env` with real API keys; set `BUDGET_USD` |
| 3 | **Claude (auto)** | Reads `CONTEXT.md` + `loop_state.md` + `SPEC.md` header — loads state |
| 4 | **Claude (auto)** | Detects incomplete `SPEC.md` → runs `/office-hours` → `/plan-ceo-review` → `/plan-eng-review` → fills §§ 2, 3, 5, 6, 8 |
| 5 | **Claude (auto)** | Invokes Auditor on all changes — `PASS` or `BLOCK` |
| 6 | **Claude (auto)** | Updates `loop_state.md`, writes first `task.md` |
| 7 | **Claude (auto)** | Outputs: *"Spec filled (Version 1). Env/Budget ready? Say 'task loop start'."* |
| 8 | You | Review `SPEC.md` + `task.md`, then say `"task loop start"` |
| 9 | You | Open `task.md` in Cursor → implement |
| 10 | You | Run: `python scripts/[script].py 2>&1 \| python scripts/summarize_run.py --task 001` |
| 11 | **Claude (auto)** | Reads `result.md` → updates `CONTEXT.md` / `loop_state.md` → Auditor gate → writes next `task.md` |
| 12 | — | Repeat steps 9–11. After 3 rounds or weekly: `/retro` + self-update rule appended to `CLAUDE.md`. |

Steps 3–7 happen automatically on every session open — no prompting required.
`repo_context.md` stays blank until code exists; fill it once the architecture stabilises.

---

## What a bootstrapped project looks like

```
my-project/
├── CLAUDE.md              ← agent instructions (session entry point)
├── repo_context.md        ← one-page architecture snapshot for cold starts
├── SPEC.md                ← source of truth: requirements, data sources, acceptance criteria
├── CONTEXT.md             ← state log: decisions, milestones, blockers
├── SKILL.md               ← reusable procedures (+ any skill packs injected here)
│
├── agent_loop/
│   ├── task.md            ← Claude writes → Cursor reads
│   ├── result.md          ← script output → Claude reads
│   ├── loop_state.md      ← current iteration snapshot
│   └── spend.log          ← cumulative API spend (append-only)
│
├── .constitution/
│   ├── MASTER_RULES.md    ← universal guardrails (read-only)
│   └── identity.md        ← owner persona (read-only)
│
├── agent/
│   ├── rules.yaml         ← code quality rules
│   ├── skills/            ← write_task, build_feature, refactor_safe, repo_map, ...
│   └── mcps/              ← 5 MCP interface configs
│
├── scripts/
│   ├── summarize_run.py       ← formats script stdout → result.md
│   ├── consult_gemini.py      ← query Gemini with project context → result.md
│   ├── consult_market.py      ← Perplexity Sonar via OpenRouter → result.md
│   ├── run_r_and_d.py         ← R&D pod runner → findings written to pod + result.md
│   └── _consult_base.py       ← shared: context loading, kill switch, spend logging
│
├── research/
│   └── notebook_sync.md   ← paste NotebookLM output here for Claude to ingest
│
├── .cursorrules           ← Cursor session entry point
├── .env                   ← secrets + kill switch budget (never commit)
├── .env.example           ← env template (committed)
└── .gitignore
```

---

## This repo's layout

```
headless_factory/
├── CLAUDE.md                    ← bootstrap procedure (Claude Code reads this)
├── MASTER_RULES.md              ← universal constitution (domain-agnostic)
├── identity.md                  ← owner persona specification
├── PORTFOLIO.md                 ← multi-project index + Lab Director pattern
│
├── templates/                   ← rendered into every bootstrapped project
│   ├── CLAUDE.md.template       ← SessionStart Autopilot + Agent Teams + Planning Skills
│   ├── SPEC.md.template
│   ├── CONTEXT.md.template
│   ├── SKILL.md.template
│   ├── repo_context.md.template
│   ├── cursorrules.template
│   ├── agent_loop/
│   │   ├── task.md.template
│   │   ├── result.md.template
│   │   └── loop_state.md.template
│   └── research/
│       └── r_and_d_pod.md.template  ← optional AutoResearch R&D Pod
│
├── agent/                       ← copied verbatim into every bootstrapped project
│   ├── rules.yaml
│   ├── skills/                  ← write_task, build_feature, refactor_safe, repo_map,
│   │                               test_generator, bug_hunt
│   └── mcps/                    ← filesystem, git, python, shell, http
│
├── skills/                      ← domain knowledge packs (opt-in at bootstrap)
│   └── valuation.md             ← DCF/NAV templates, Decimal arithmetic, sensitivity analysis
│
├── scripts/
│   ├── summarize_run.py         ← formats script stdout → agent_loop/result.md  [copied to projects]
│   ├── consult_gemini.py        ← Gemini 2.0 Flash consult with project context  [copied to projects]
│   ├── consult_market.py        ← Perplexity Sonar via OpenRouter (live web search)  [copied to projects]
│   ├── run_r_and_d.py           ← R&D pod runner: reads pod, calls Gemini, writes findings  [copied to projects]
│   ├── _consult_base.py         ← shared utilities (context, kill switch, spend log)  [copied to projects]
│   └── portfolio_report.py      ← factory-only: aggregates spend + status across all projects
│
└── research/
    └── notebook_sync.md         ← NotebookLM handoff template
```

---

## Three governance layers

| Layer | File | Scope |
|-------|------|-------|
| Universal guardrails | `MASTER_RULES.md` | All projects — plan-before-act, kill switch, atomic writes, code quality |
| Owner identity | `identity.md` | Personal profile and hard limits — read by agent, not directives |
| Domain skill packs | `skills/*.md` | Opt-in — appended to `SKILL.md` only when requested at bootstrap |

---

## The dev loop

```
SESSION OPEN (automatic)
────────────────────────────────────────────────────────────
Claude loads: CONTEXT.md + loop_state.md + SPEC.md header
        ↓
SPEC §§ 2,3,5,6,8 incomplete?
  YES → /office-hours → /plan-ceo-review → /plan-eng-review → fill SPEC + repo_context
  NO  → continue
        ↓
Auditor gate (5 Hard Limits) → PASS or BLOCK
        ↓
Update loop_state.md → write task.md
        ↓
Output: "Spec filled (Version N). Say 'task loop start'."

TASK LOOP (after "task loop start")
────────────────────────────────────────────────────────────
1. Cursor reads task.md + listed files → implements
        ↓
2a. Run local script:
    python scripts/[script].py 2>&1 | python scripts/summarize_run.py --task [id]
        ↓  OR
2b. Run external consult:
    python scripts/consult_gemini.py "your question" --task [id]
    python scripts/consult_market.py "market intelligence query" --task [id]
        ↓  OR
2c. Run R&D pod:
    python scripts/run_r_and_d.py research/r_and_d_pod.md --task [id]
        ↓
3. Claude reads result.md → updates CONTEXT.md + loop_state.md
        ↓
4. Auditor gate on changes → write next task.md
        ↓
   (repeat from 1)

SELF-UPDATE (every 3 rounds or /retro)
────────────────────────────────────────────────────────────
Claude scans transcript → appends "# Learned: [rule]" to CLAUDE.md → commits
```

Token budget per loop: ~2–4k on cold start, ~1–2k per result read.

---

## External consult scripts

Both scripts automatically attach `repo_context.md` + `SPEC.md` as context and prepend
`identity.md` Hard Limits to the system prompt. Output goes to `agent_loop/result.md`.

```bash
# Strategic / analytical queries
python scripts/consult_gemini.py "Audit this valuation logic" --task 003
python scripts/consult_gemini.py "What are the key risks in this model?" --model gemini-2.5-pro

# Live market intelligence (web search)
python scripts/consult_market.py "Current DCF discount rates for Asian infrastructure"
python scripts/consult_market.py "Tokenised real estate liquidity risks 2025" --task 004
```

Requires in `.env`:
```
GEMINI_API_KEY=...
OPENROUTER_API_KEY=...
```

API spend is tracked per-call in `agent_loop/spend.log` and enforced against `BUDGET_USD`.

---

## NotebookLM handoff

1. Paste NotebookLM synthesis into `research/notebook_sync.md`
2. Tell Claude Code: `"read the notebook sync"`
3. Claude ingests it and continues the dev loop

---

## Agent Teams

Every bootstrapped project's `CLAUDE.md` defines two sub-agent roles, invoked via the `Agent` tool:

| Role | Trigger | What it does |
|------|---------|-------------|
| **Researcher** | External fact-gathering needed | Searches, cites sources, writes `research/[topic]-[date].md`, returns confidence-tagged summary |
| **Auditor** | Before any `project_plan.md` is finalised, or before any irreversible action | Checks all 5 identity.md Hard Limits — outputs `PASS` with evidence or `BLOCK` with violations |

The Auditor's five checks (from `identity.md`):
1. Risk register present — bear case is the anchor
2. No float for money — Decimal confirmed
3. Every output states methodology and assumptions
4. API spend tracked; no call exceeds `BUDGET_USD` without confirmation
5. No range too wide to be decision-relevant

A `BLOCK` halts execution. Nothing proceeds past it without resolving the violation.

---

## Planning Skills (gstack)

If gstack is installed (`~/.claude/skills/gstack/`), these skills map to project phases:

| Skill | Phase | Purpose |
|-------|-------|---------|
| `/office-hours` | Before `SPEC.md` | Expose demand reality, narrow scope, surface hidden assumptions |
| `/plan-ceo-review` | After first plan draft | Strategic review — expand, reduce, or rethink premises |
| `/plan-eng-review` | Before first Cursor task | Lock in architecture, data flow, edge cases, test coverage |
| `/retro` | End of sprint / week | Commit history analysis, per-person breakdown, trend tracking |

Check gstack is installed: `ls ~/.claude/skills/gstack/SKILL.md 2>/dev/null && echo installed`

---

## AutoResearch R&D Pod

For projects requiring structured external research, copy the template into the project:

```bash
cp [factory]/templates/research/r_and_d_pod.md.template [project]/research/r_and_d_pod.md
```

Fill in the Query block (topic, decision it supports, 3 specific questions), then tell Claude:
`"activate the R&D pod"`. The Researcher sub-agent runs, cites sources with confidence levels,
and writes findings back into the same file.

---

## Running multiple projects

The factory doubles as a **Lab Director** for a portfolio of active headless projects.

**Portfolio index**: `PORTFOLIO.md` (factory root) — one row per project, manually updated
at bootstrap/archive/kill. Run `python scripts/portfolio_report.py` to refresh spend and
status automatically.

**Lab Director session** — open the factory in Claude Code and say:

```
"Act as Lab Director. Read PORTFOLIO.md and scan each active project's
CONTEXT.md, loop_state.md, and spend.log. Report status, flag blockers,
and recommend where attention is needed most."
```

Claude reads each project's `loop_state.md` + `CONTEXT.md` + `spend.log` and returns a
prioritised attention table. No API calls to external LLMs — pure file reads.

**Attention priority order**: BLOCKED → budget > 80% → stale (> 7 days) → lifecycle drift → active build.

**Lifecycle states** (tracked in `SPEC.md` and `CONTEXT.md` per project):

| State | Meaning |
|-------|---------|
| `ACTIVE` | In development |
| `MAINTENANCE` | Acceptance criteria met; no new features |
| `ARCHIVED` | Stable, no changes; kept for reference |
| `KILLED` | Kill conditions met; stopped |

The Auditor sub-agent checks lifecycle status before approving new work — it blocks new tasks
on `MAINTENANCE` or `ARCHIVED` projects unless the user explicitly overrides.

---

## Agent Teams SOP

Agent Teams are invoked **within a Claude Code session** using the `Agent` tool.
There is no persistent background daemon — each invocation is scoped to the current session.

### Invoking the Researcher

Tell Claude (in the project's Claude Code session):

```
"Invoke the Researcher to find [topic]. Write findings to research/[topic]-today.md."
```

Claude spawns a Researcher subagent that searches, cites sources with confidence levels
(HIGH/MEDIUM/LOW), writes the findings file, and returns a summary.

For a structured multi-question research run, activate the R&D pod first:
```bash
cp [factory]/templates/research/r_and_d_pod.md.template research/r_and_d_pod.md
# fill in the Query block, then:
python scripts/run_r_and_d.py research/r_and_d_pod.md --task 005
```

### Invoking the Auditor

The Auditor is triggered automatically before `project_plan.md` is finalised.
To invoke manually:

```
"Run the Auditor on the current plan."
```

Claude spawns an Auditor subagent that reads `.constitution/identity.md` Hard Limits and
returns `PASS — [evidence]` or `BLOCK — [violations]`. A BLOCK stops execution.

### Weekly retro (background-friendly)

```
"Run /retro for this project."
```

Analyses commit history, per-contributor breakdown, trend tracking. No external API needed.
Run from inside the project's Claude Code session.

---

## Adding a skill pack

1. Create `skills/<name>.md` with domain-specific procedures and code patterns
2. Reference at bootstrap: `"bootstrap X with the <name> skill"`
3. To inject into an existing project: append `skills/<name>.md` to that project's `SKILL.md`
