# Skill: repo_map

> Use to understand an unfamiliar repo or re-orient after a gap.

---

## Trigger

"map the repo", "what does this repo do", "orient me", "where is X", "how does Y work"

---

## Workflow

### 1. Scan structure
- List all top-level dirs and their apparent purpose.
- Identify which folders match the standard layout (src, scripts, tests, agent, modules, skills).
- Flag any folders that don't fit — they may be legacy or undocumented.

### 2. Find entry points
- Look for: `main.py`, `index.*`, `cli.py`, `run.py`, `Makefile`, `scripts/`, `package.json#scripts`.
- Read the first 30 lines of each entry point.
- Identify what triggers execution (CLI arg, import, cron, etc.).

### 3. Trace data flow
- Start from the entry point.
- Follow: input → transformation → output.
- Note where external state is touched (DB, API, filesystem, env vars).

### 4. Identify dependencies
- Check: `pyproject.toml`, `package.json`, `requirements.txt`, `Cargo.toml`, etc.
- List direct dependencies only (not transitive).
- Flag anything unusual or heavy.

### 5. Output the map
Produce a concise summary:

```
ENTRY POINTS
  scripts/run.py      → CLI, calls src/pipeline.py
  src/api.py          → FastAPI app, mounted at /

KEY MODULES
  src/pipeline.py     → core ETL logic
  src/models.py       → data models
  src/io.py           → file read/write (atomic writes)

EXTERNAL STATE
  .env                → BUDGET_USD, API keys
  data/raw/           → input CSVs
  outputs/            → generated reports

DEPENDENCIES
  pandas, httpx, pydantic (pyproject.toml)

GAPS / UNKNOWNS
  legacy/ folder — unclear purpose, no tests
```

---

## Hard stops

- Do not guess at purpose — read the actual files.
- Flag gaps explicitly rather than filling them with assumptions.
