# Bootstrap Procedure — Steps 1–8

Full 8-step procedure executed by `/bootstrap`. See `bootstrap.md` for field collection.

---

## Step 1 — Create directory structure

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

---

## Step 2 — Copy static files (no substitution)

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

---

## Step 3 — Render all templates (with variable substitution)

Read each template, apply the variable map (see Step 4), and write to target:

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

---

## Step 4 — Variable substitution map

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

---

## Step 5 — Write environment files

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

---

## Step 6 — Write .gitignore

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

---

## Step 7 — Initialize git and connect GitHub

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

---

## Step 8 — Confirm and report

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
