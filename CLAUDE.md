# Workflow Starter — Bootstrap Toolkit

This repo is a project initialization toolkit for Claude Code and Cursor. It defines standardized
guardrails, planning discipline, and domain skill packs that get stamped into every new project.

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

Then execute the procedure below without further prompting.

---

## Bootstrap Procedure

### Step 1 — Create directory structure

```
[target_dir]/
├── CLAUDE.md              ← session entry point; read repo_context.md first
├── repo_context.md        ← one-page architecture snapshot; Claude reads this on cold start
├── SPEC.md                ← stable requirements (rarely read mid-loop)
├── CONTEXT.md             ← architecture decisions + milestones only (no session log)
├── SKILL.md               ← domain procedures (read by Cursor, not Claude mid-loop)
│
├── agent_loop/            ← loop artifacts; all files overwritten each iteration
│   ├── task.md            ← Claude writes → Cursor reads
│   ├── result.md          ← summarize_run.py writes → Claude reads
│   └── loop_state.md      ← current iteration snapshot
│
├── .constitution/
│   ├── MASTER_RULES.md    ← copied from toolkit (read-only)
│   └── identity.md        ← copied from toolkit (read-only)
├── agent/                 ← copied from toolkit
│   ├── rules.yaml
│   ├── skills/            ← all workflow skill files (including write_task)
│   └── mcps/              ← all 5 MCP configs
├── src/                   ← source code
├── scripts/
│   └── summarize_run.py   ← formats execution output → agent_loop/result.md
├── tests/                 ← unit tests
├── modules/               ← optional extensions
├── .cursorrules           ← Cursor reads this at session start instead of manual setup
├── .env                   ← secrets — NEVER commit
├── .env.example           ← env template — commit this
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
| `{{PROJECT_NOTES}}` | *(leave blank)* |

### Step 5 — Write environment files

**.env** (do NOT stage in git):
```
# DO NOT COMMIT — copy of .env.example with real values
BUDGET_USD=[budget]
LOG_LEVEL=INFO
```

**.env.example** (stage in git):
```
# Copy to .env and fill in values. NEVER commit .env.

# Kill Switch — max API spend per session (USD)
BUDGET_USD=5.00

# Logging
LOG_LEVEL=INFO

# Add project-specific secrets below:
# ANTHROPIC_API_KEY=
# OPENAI_API_KEY=
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
    scripts/ src/ tests/ modules/ \
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
- Budget configured
- GitHub: remote URL if created, or "skipped — run `gh auth login` to enable"

Then output this exact block so the user knows what needs their input:

---
**Bootstrap complete. Two files need your input before work can start:**

**1. `SPEC.md` — fill this now** *(required before any task can be written)*
   - [ ] § 2 Scope — what's in and out
   - [ ] § 3 Data Sources — where data comes from
   - [ ] § 5 Inputs & Outputs — what goes in, what comes out
   - [ ] § 6 Acceptance Criteria — how you'll know it's done
   - [ ] § 8 Hardware Target — CPU-only, NVIDIA, or Apple Silicon

**2. `repo_context.md` — fill this once code exists** *(leave blank for now)*
   - Entry points, key modules, data flow, how to run

**Everything else fills itself as work progresses.**
Say "help me fill out SPEC.md" to do it now in chat.
---

---

## Dev Loop (how active projects run)

The intended cycle for all bootstrapped projects:

```
1. Claude reads repo_context.md + agent_loop/loop_state.md
        ↓
2. Claude writes agent_loop/task.md   [skill: write_task]
        ↓
3. Cursor reads agent_loop/task.md + listed files → implements
        ↓
4. Developer runs script locally:
   python scripts/[script].py 2>&1 | python scripts/summarize_run.py --task [id]
        ↓
5. Claude reads agent_loop/result.md → writes next task
        ↓
   (repeat)
```

**Token budget per loop:**
- Claude cold start: `repo_context.md` + `loop_state.md` (~2–4k tokens)
- Cursor per task: `task.md` + listed files only (no full repo read)
- Claude per result: `result.md` only (~1–2k tokens)

---

## Agent Layer (active in this repo and all bootstrapped projects)

### Workflow Skills
Invoke by name when starting a task:

| Skill | File | When to use |
|-------|------|-------------|
| `write_task` | `agent/skills/write_task.md` | Writing the next task for Cursor (use before every handoff) |
| `build_feature` | `agent/skills/build_feature.md` | Implementing new behaviour |
| `refactor_safe` | `agent/skills/refactor_safe.md` | Improving structure without changing behaviour |
| `repo_map` | `agent/skills/repo_map.md` | Orienting in an unfamiliar repo |
| `test_generator` | `agent/skills/test_generator.md` | Writing or expanding test coverage |
| `bug_hunt` | `agent/skills/bug_hunt.md` | Investigating a failure or unexpected output |

### Code Rules
`agent/rules.yaml` — read before writing or modifying any code:
- Functions ≤ 30 lines, nesting ≤ 3 levels
- snake_case, descriptive names
- No hidden state, no silent fallbacks, no bare except
- No float for money; no hardcoded secrets

### MCP Interfaces
`agent/mcps/` — defines scope and constraints for each integration:

| Config | Purpose |
|--------|---------|
| `filesystem.yaml` | Scoped file read/write |
| `git.yaml` | Git operations with confirmation gates |
| `python.yaml` | Python runtime (uv preferred) |
| `shell.yaml` | Bash execution limits |
| `http.yaml` | Outbound API calls (domain allowlist required) |

---

## Constitutional Rules (applied to all bootstrapped projects)

These rules live in `MASTER_RULES.md` and are copied into every project's `.constitution/`.
The most critical — enforce these during bootstrap and remind the project agent to read them:

1. **Plan before act** — no file writes without a `project_plan.md` containing all 5 required sections
2. **Kill switch** — track API spend; halt when `BUDGET_USD` is reached
3. **Secrets in .env only** — never hardcode, never commit
4. **Atomic writes** — write to `.tmp`, validate non-empty, rename to target

---

## Available Skill Packs

| Skill name | File | What it adds |
|-----------|------|-------------|
| `valuation` | `skills/valuation.md` | DCF/NAV templates, Decimal arithmetic, sensitivity analysis |

To add more skill packs: create a `.md` file in `skills/` and reference it by filename stem.

To inject a skill pack into an existing project: append `skills/[name].md` to that project's `SKILL.md`.

---

## Repo Layout (this toolkit)

```
/
├── CLAUDE.md                    ← you are here
├── MASTER_RULES.md              ← universal constitution
├── identity.md                  ← default agent persona
│
├── agent/                       ← agent layer (always active)
│   ├── rules.yaml               ← code quality rules
│   ├── skills/
│   │   ├── write_task.md        ← Claude→Cursor handoff format
│   │   ├── build_feature.md
│   │   ├── refactor_safe.md
│   │   ├── repo_map.md
│   │   ├── test_generator.md
│   │   └── bug_hunt.md
│   └── mcps/
│       ├── filesystem.yaml
│       ├── git.yaml
│       ├── python.yaml
│       ├── shell.yaml
│       └── http.yaml
│
├── skills/                      ← domain knowledge packs (injected at bootstrap)
│   └── valuation.md
│
├── templates/                   ← all templates rendered during bootstrap
│   ├── CLAUDE.md.template
│   ├── SPEC.md.template
│   ├── CONTEXT.md.template
│   ├── SKILL.md.template
│   ├── repo_context.md.template
│   ├── cursorrules.template     ← becomes .cursorrules in every project
│   └── agent_loop/
│       ├── task.md.template
│       ├── result.md.template
│       └── loop_state.md.template
├── modules/                     ← optional extensions (empty — add as needed)
├── src/                         ← project logic (empty — fill per project)
├── scripts/
│   └── summarize_run.py         ← formats CLI output → agent_loop/result.md
├── tests/                       ← unit tests (empty — fill per project)
└── .gitignore
```
