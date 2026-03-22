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

---

## How to use

Open this repo in Claude Code and trigger with any of:

```
"bootstrap a new project"
"init a project called <name>"
"spin up <name>"
"new project called <name>"
```

Claude will ask for any missing required fields (name, purpose) then execute the full
bootstrap procedure documented in `CLAUDE.md` — no further prompting needed.

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
│   └── loop_state.md      ← current iteration snapshot
│
├── .constitution/
│   ├── MASTER_RULES.md    ← universal guardrails (copied from toolkit, read-only)
│   └── identity.md        ← owner persona (copied from toolkit, read-only)
│
├── agent/
│   ├── rules.yaml         ← code quality rules
│   ├── skills/            ← workflow skill files
│   └── mcps/              ← 5 MCP interface configs
│
├── .cursorrules           ← Cursor session entry point
├── .env                   ← secrets + kill switch budget (never commit)
├── .env.example           ← env template (committed)
├── .gitignore
├── src/
├── scripts/
│   └── summarize_run.py
└── tests/
```

---

## This repo's layout

```
headless_factory/
├── CLAUDE.md              ← bootstrap procedure (Claude Code reads this)
├── MASTER_RULES.md        ← universal constitution (domain-agnostic)
├── identity.md            ← owner persona specification
│
├── templates/             ← rendered into every bootstrapped project
│   ├── CLAUDE.md.template
│   ├── SPEC.md.template
│   ├── CONTEXT.md.template
│   ├── SKILL.md.template
│   ├── repo_context.md.template
│   ├── cursorrules.template
│   └── agent_loop/
│       ├── task.md.template
│       ├── result.md.template
│       └── loop_state.md.template
│
├── agent/                 ← copied verbatim into every bootstrapped project
│   ├── rules.yaml
│   ├── skills/            ← write_task, build_feature, refactor_safe, repo_map, ...
│   └── mcps/              ← filesystem, git, python, shell, http
│
├── skills/                ← domain knowledge packs (opt-in at bootstrap)
│   └── valuation.md       ← DCF/NAV templates, Decimal arithmetic, sensitivity analysis
│
└── scripts/
    └── summarize_run.py   ← formats script output → agent_loop/result.md
```

---

## Three governance layers

| Layer | File | Scope |
|-------|------|-------|
| Universal guardrails | `MASTER_RULES.md` | All projects — plan-before-act, kill switch, atomic writes, code quality |
| Owner identity | `identity.md` | Personal profile and hard limits — reference, not directives |
| Domain skill packs | `skills/*.md` | Opt-in — appended to `SKILL.md` only when requested |

---

## The dev loop (how active projects run)

```
1. Claude reads repo_context.md + agent_loop/loop_state.md
        ↓
2. Claude writes agent_loop/task.md
        ↓
3. Cursor reads task.md + listed files → implements
        ↓
4. Developer runs script:
   python scripts/[script].py 2>&1 | python scripts/summarize_run.py --task [id]
        ↓
5. Claude reads agent_loop/result.md → writes next task
        ↓
   (repeat)
```

Token budget per loop: ~2–4k on cold start, ~1–2k per result read.

---

## Adding a skill pack

1. Create `skills/<name>.md` with domain-specific procedures and code patterns.
2. Reference it at bootstrap: "bootstrap X with the `<name>` skill"
3. To inject into an existing project: append `skills/<name>.md` to that project's `SKILL.md`.
