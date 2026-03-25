# Headless Factory — Bootstrap Toolkit

This repo spins up new AI-assisted projects with consistent structure, governance, and guardrails.
Claude Code reads this file and executes bootstraps on demand. No CLI, no Python, no setup required.

---

## How to Bootstrap a New Project

**Trigger phrases**: "init a project", "bootstrap", "create a new project", "start a new repo",
"spin up [name]", "new project called [name]"

When triggered, collect the following. Ask for missing required fields in a single message —
never ask one field at a time. If purpose is obvious from context, infer it.

| Field | Required | Default |
|-------|----------|---------|
| `name` | Yes | — |
| `purpose` | Yes | — |
| `target_dir` | Yes | ask — do not assume |
| `github` | Yes | ask — `private`, `public`, or `none` |
| `skills` | No | none (options: `valuation`) |
| `budget` | No | `5.00` |

Then execute the full procedure below without further prompting.

---

## Bootstrap Procedure

### Step 1 — Create directory structure

```
[target_dir]/
├── CLAUDE.md              ← session entry point (rendered from template)
├── repo_context.md        ← one-page architecture snapshot; Claude reads on cold start
├── SPEC.md                ← source of truth: requirements, lifecycle, acceptance criteria
├── CONTEXT.md             ← architecture decisions + milestones + lifecycle status
├── SKILL.md               ← domain procedures + universal patterns
│
├── agent_loop/
│   ├── task.md            ← Claude writes → Cursor reads
│   ├── result.md          ← script/consult output → Claude reads
│   ├── loop_state.md      ← current iteration snapshot (overwritten each iteration)
│   └── spend.log          ← append-only API spend log (JSONL)
│
├── .constitution/
│   ├── MASTER_RULES.md    ← universal guardrails (read-only)
│   └── identity.md        ← owner persona + Hard Limits (read-only)
│
├── agent/
│   ├── rules.yaml         ← code quality rules
│   ├── skills/            ← write_task, build_feature, refactor_safe, repo_map,
│   │                         test_generator, bug_hunt
│   └── mcps/              ← filesystem, git, python, shell, http configs
│
├── scripts/
│   ├── summarize_run.py       ← formats script stdout → agent_loop/result.md
│   ├── _consult_base.py       ← shared: project context, kill switch, spend logging
│   ├── consult_gemini.py      ← query Gemini 2.0 Flash with project context
│   ├── consult_market.py      ← Perplexity Sonar via OpenRouter (live web search)
│   └── run_r_and_d.py         ← R&D pod runner: reads pod → Gemini → findings
│
├── research/
│   └── notebook_sync.md       ← paste NotebookLM synthesis here for Claude to ingest
│
├── src/                   ← source code
├── tests/                 ← unit tests
├── modules/               ← optional extensions
├── .cursorrules           ← Cursor session entry point
├── .env                   ← secrets + kill switch budget (NEVER commit)
├── .env.example           ← env template (commit this)
└── .gitignore
```

If skills include `valuation`, also create:
```
data/raw/
data/processed/
outputs/
```

### Step 2 — Copy static files (no substitution)

Copy verbatim from THIS repo into target:
- `MASTER_RULES.md` → `[target]/.constitution/MASTER_RULES.md`
- `identity.md` → `[target]/.constitution/identity.md`
- `agent/` → `[target]/agent/` (entire directory — rules, skills, mcps)
- `scripts/summarize_run.py` → `[target]/scripts/summarize_run.py`
- `scripts/_consult_base.py` → `[target]/scripts/_consult_base.py`
- `scripts/consult_gemini.py` → `[target]/scripts/consult_gemini.py`
- `scripts/consult_market.py` → `[target]/scripts/consult_market.py`
- `scripts/run_r_and_d.py` → `[target]/scripts/run_r_and_d.py`
- `research/notebook_sync.md` → `[target]/research/notebook_sync.md`

After copying, update `[target]/agent/mcps/filesystem.yaml` and `python.yaml`:
replace the placeholder `"/path/to/project/root"` with the actual `[target]` absolute path.

### Step 3 — Render all templates (with variable substitution)

Read each template, apply the variable map (see §Step 4), and write to target:

| Template | Target |
|----------|--------|
| `templates/CLAUDE.md.template` | `[target]/CLAUDE.md` |
| `templates/SPEC.md.template` | `[target]/SPEC.md` |
| `templates/CONTEXT.md.template` | `[target]/CONTEXT.md` |
| `templates/SKILL.md.template` | `[target]/SKILL.md` |
| `templates/repo_context.md.template` | `[target]/repo_context.md` |
| `templates/cursorrules.template` | `[target]/.cursorrules` |
| `templates/agent_loop/task.md.template` | `[target]/agent_loop/task.md` |
| `templates/agent_loop/result.md.template` | `[target]/agent_loop/result.md` |
| `templates/agent_loop/loop_state.md.template` | `[target]/agent_loop/loop_state.md` |

If skills were requested, append `skills/[skill].md` content in place of `{{SKILL_PACK_CONTENT}}`
in SKILL.md. If no skills, replace with `*(No skill packs loaded.)*`.

**Optional R&D Pod** — if the user requests research/AutoResearch capability, also copy:
`templates/research/r_and_d_pod.md.template` → `[target]/research/r_and_d_pod.md`
(Fill in the Query block and run `python scripts/run_r_and_d.py` to activate.)

### Step 4 — Variable substitution map

Replace every occurrence of these tokens across ALL generated files:

| Token | Replace with |
|-------|-------------|
| `{{PROJECT_NAME}}` | project name (slug, e.g. `dcf-analysis`) |
| `{{DATE}}` | today's date, YYYY-MM-DD |
| `{{PROJECT_PURPOSE}}` | purpose statement (one sentence) |
| `{{PROJECT_ROOT}}` | absolute path to project directory |
| `{{SKILLS_LOADED}}` | skill names comma-separated, or `none` |
| `{{SKILL_PACK_CONTENT}}` | concatenated skill pack file contents |
| `{{TASK_ID}}` | `1` (first task; increment each iteration) |
| `{{PROJECT_NOTES}}` | `*(Add project-specific notes here after bootstrap.)*` |

### Step 5 — Write environment files

**.env** (do NOT stage in git):
```
# DO NOT COMMIT — copy of .env.example with real values
BUDGET_USD=[budget]
LOG_LEVEL=INFO
GEMINI_API_KEY=
OPENROUTER_API_KEY=
```

**.env.example** (stage in git):
```
# Copy to .env and fill in values. NEVER commit .env.

# Kill Switch — max API spend per session (USD)
BUDGET_USD=5.00

# Logging
LOG_LEVEL=INFO

# External Consult APIs
GEMINI_API_KEY=
OPENROUTER_API_KEY=

# Add project-specific secrets below:
# ANTHROPIC_API_KEY=
```

### Step 6 — Write .gitignore

```
.env
.env.*
!.env.example
__pycache__/
*.pyc
*.pyo
.venv/
venv/
node_modules/
*.egg-info/
dist/
build/
*.tmp
*.log
.DS_Store
Thumbs.db
```

### Step 7 — Initialize git and connect GitHub

```bash
git init [target_dir]
git -C [target_dir] add \
    CLAUDE.md SPEC.md CONTEXT.md SKILL.md repo_context.md .cursorrules \
    .constitution/ agent/ agent_loop/ \
    scripts/ src/ tests/ modules/ research/ \
    .env.example .gitignore
git -C [target_dir] commit -m "chore: bootstrap [name]"
```

If git commit fails due to missing user config, warn but do not halt.

**If `github` ≠ `none`**, create the remote repo and push:
```bash
gh repo create [name] --[private|public] --source [target_dir] --remote origin --push
```

If `gh` is not authenticated, output this warning and skip — do not halt:
> GitHub step skipped: run `gh auth login` then `gh repo create [name] --private --source . --remote origin --push` from the project directory.

### Step 8 — Confirm

Report:
- Files created (list)
- Skills loaded
- Budget configured: `$[budget]`
- GitHub: remote URL if created, or skip message

Check gstack:
```bash
ls ~/.claude/skills/gstack/SKILL.md 2>/dev/null && echo "gstack: ready" || echo "gstack: not found"
```
If not found: "Planning skills unavailable — install gstack: `cd ~/.claude/skills/gstack && ./setup`"

**Update PORTFOLIO.md in the factory repo**: add a row for the new project to the Active Projects table.

Then output this block:

---
**Bootstrap complete.**

**Immediate actions:**
1. Open `[target_dir]` in Claude Code — the SessionStart Autopilot will drive SPEC.md planning automatically
2. Fill `.env` with real API keys (`GEMINI_API_KEY`, `OPENROUTER_API_KEY`)
3. Say `"task loop start"` once SPEC is confirmed to begin implementation

**Files that need your input:**
- `SPEC.md` §§ 2, 3, 5, 6, 8 — scope, data sources, I/O, acceptance, hardware target
- `repo_context.md` — fill once code exists (leave blank for now)

Everything else runs automatically via the SessionStart Autopilot.
---

---

## Dev Loop (how active projects run)

Every bootstrapped project's `CLAUDE.md` contains a **SessionStart Autopilot** that
self-drives session startup. The full cycle:

```
SESSION OPEN (automatic — driven by SessionStart Autopilot in project CLAUDE.md)
──────────────────────────────────────────────────────────────────────────────
Claude loads: CONTEXT.md + agent_loop/loop_state.md + SPEC.md header
      ↓
SPEC §§ 2,3,5,6,8 incomplete?
  YES → /office-hours → /plan-ceo-review → /plan-eng-review → fill SPEC + repo_context
  NO  → continue
      ↓
Auditor sub-agent: checks 5 Hard Limits from .constitution/identity.md
  BLOCK → explain → halt
  PASS  → continue
      ↓
Update loop_state.md → write agent_loop/task.md
      ↓
Output: "Spec filled (Version N). Say 'task loop start'."

TASK LOOP (after "task loop start")
──────────────────────────────────────────────────────────────────────────────
1. Cursor reads task.md + listed files → implements
      ↓
2. Developer runs one of:
   python scripts/[script].py 2>&1 | python scripts/summarize_run.py --task [id]
   python scripts/consult_gemini.py "question" --task [id]
   python scripts/consult_market.py "market query" --task [id]
   python scripts/run_r_and_d.py research/r_and_d_pod.md --task [id]
      ↓
3. Claude reads agent_loop/result.md
      ↓
4. Auditor gate on changes → update CONTEXT.md + loop_state.md → write next task.md
      ↓
   (repeat from 1)

SELF-UPDATE (every 3 rounds or /retro)
──────────────────────────────────────────────────────────────────────────────
Claude scans transcript → appends "# Learned: [rule]" to project CLAUDE.md → commits
```

**Token budget per loop:**
- Cold start: `repo_context.md` + `loop_state.md` (~2–4k tokens)
- Per result read: `result.md` only (~1–2k tokens)
- Cursor per task: `task.md` + listed files only

---

## External Consult Scripts

All scripts attach `repo_context.md` + `SPEC.md` as context and prepend `identity.md`
Hard Limits to the system prompt. Output always goes to `agent_loop/result.md`.
API spend is tracked per-call in `agent_loop/spend.log` against `BUDGET_USD`.

| Script | Purpose | Key env var |
|--------|---------|-------------|
| `consult_gemini.py "query" --task N` | Analytical queries, code audit, risk review | `GEMINI_API_KEY` |
| `consult_market.py "query" --task N` | Live market data, competitor intel (Perplexity Sonar) | `OPENROUTER_API_KEY` |
| `run_r_and_d.py [pod_path] --task N` | Structured multi-question research via R&D pod | `GEMINI_API_KEY` |
| `summarize_run.py --task N` | Format script stdout → result.md (pipe target, not called directly) | — |

---

## Portfolio Management

This factory repo also serves as a **Lab Director** for all active projects.

**`PORTFOLIO.md`** (this repo root) — one row per project. Update manually at bootstrap/archive/kill.
**`scripts/portfolio_report.py`** — factory-only script that aggregates lifecycle status, spend,
and blockers across all projects.

```bash
# Scan specific projects
python scripts/portfolio_report.py --paths ../project-a ../project-b

# Scan all projects from PORTFOLIO.md
python scripts/portfolio_report.py --from-portfolio --output portfolio_status.md
```

To run a Lab Director session, open this repo in Claude Code and say:
`"Act as Lab Director. Read PORTFOLIO.md and scan each active project."`

---

## Agent Layer (active in this repo and all bootstrapped projects)

### Workflow Skills
Invoke by name when needed:

| Skill | File | When to use |
|-------|------|-------------|
| `write_task` | `agent/skills/write_task.md` | Writing the next task for Cursor |
| `build_feature` | `agent/skills/build_feature.md` | Implementing new behaviour |
| `refactor_safe` | `agent/skills/refactor_safe.md` | Improving structure without changing behaviour |
| `repo_map` | `agent/skills/repo_map.md` | Orienting in an unfamiliar repo |
| `test_generator` | `agent/skills/test_generator.md` | Writing or expanding test coverage |
| `bug_hunt` | `agent/skills/bug_hunt.md` | Investigating a failure or unexpected output |

### Agent Teams (in every bootstrapped project)

| Role | Trigger | What it does |
|------|---------|-------------|
| **Researcher** | External fact-gathering needed | Searches, cites sources with confidence levels, writes `research/[topic]-[date].md` |
| **Auditor** | Before any plan is finalised; before any irreversible action | Checks all 5 `identity.md` Hard Limits — `PASS` or `BLOCK` |

### Planning Skills (gstack — if installed)

| Skill | Phase |
|-------|-------|
| `/office-hours` | Before writing SPEC.md |
| `/plan-ceo-review` | After first plan draft |
| `/plan-eng-review` | Before first Cursor task |
| `/retro` | End of sprint / week |

### Code Rules
`agent/rules.yaml` — read before writing or modifying any code:
- Functions ≤ 30 lines, nesting ≤ 3 levels, snake_case
- No hidden state, no silent fallbacks, no bare except
- No float for money; no hardcoded secrets

### MCP Interfaces
`agent/mcps/` — scope and constraints per integration:

| Config | Purpose |
|--------|---------|
| `filesystem.yaml` | Scoped file read/write |
| `git.yaml` | Git operations with confirmation gates |
| `python.yaml` | Python runtime (uv preferred) |
| `shell.yaml` | Bash execution limits |
| `http.yaml` | Outbound API calls (domain allowlist required) |

---

## Constitutional Rules (applied to all bootstrapped projects)

Defined in `MASTER_RULES.md` — copied into every project's `.constitution/`:

1. **Plan before act** — no file writes without `project_plan.md` with all 5 required sections
2. **Kill switch** — track API spend against `BUDGET_USD`; halt on breach
3. **Secrets in .env only** — never hardcode, never commit
4. **Atomic writes** — write to `.tmp`, validate non-empty, rename to target

---

## Available Skill Packs

| Skill name | File | What it adds |
|-----------|------|-------------|
| `valuation` | `skills/valuation.md` | DCF/NAV templates, Decimal arithmetic, sensitivity analysis |

To add more skill packs: create a `.md` file in `skills/` and reference it by filename stem.
To inject into an existing project: append `skills/[name].md` to that project's `SKILL.md`.

---

## Repo Layout (this toolkit)

```
headless_factory/
├── CLAUDE.md                    ← you are here — bootstrap procedure + factory instructions
├── MASTER_RULES.md              ← universal constitution (domain-agnostic)
├── identity.md                  ← owner persona + Hard Limits
├── PORTFOLIO.md                 ← multi-project index + Lab Director pattern
│
├── templates/                   ← rendered into every bootstrapped project
│   ├── CLAUDE.md.template       ← SessionStart Autopilot + Agent Teams + Planning Skills
│   ├── SPEC.md.template         ← requirements + lifecycle fields
│   ├── CONTEXT.md.template      ← state log + lifecycle status
│   ├── SKILL.md.template        ← universal patterns + project procedures
│   ├── repo_context.md.template ← one-page architecture snapshot
│   ├── cursorrules.template     ← Cursor session entry point
│   ├── agent_loop/
│   │   ├── task.md.template
│   │   ├── result.md.template
│   │   └── loop_state.md.template
│   └── research/
│       └── r_and_d_pod.md.template  ← optional AutoResearch R&D pod
│
├── agent/                       ← copied verbatim into every bootstrapped project
│   ├── rules.yaml
│   ├── skills/                  ← write_task, build_feature, refactor_safe, repo_map,
│   │                               test_generator, bug_hunt
│   └── mcps/                    ← filesystem, git, python, shell, http
│
├── skills/                      ← domain knowledge packs (opt-in at bootstrap)
│   └── valuation.md
│
├── scripts/                     ← copied into every bootstrapped project (except portfolio_report.py)
│   ├── summarize_run.py         ← formats stdout → agent_loop/result.md
│   ├── _consult_base.py         ← shared: context loading, kill switch, spend logging
│   ├── consult_gemini.py        ← Gemini 2.0 Flash consult with project context
│   ├── consult_market.py        ← Perplexity Sonar via OpenRouter
│   ├── run_r_and_d.py           ← R&D pod runner
│   └── portfolio_report.py      ← factory-only: cross-project status roll-up
│
├── research/
│   └── notebook_sync.md         ← paste NotebookLM output here for Claude to ingest
│
├── src/                         ← factory source (currently empty)
├── tests/                       ← factory tests (currently empty)
└── modules/                     ← optional extensions
```
