Act as Lab Director for the Headless Factory.

1. Read `PORTFOLIO.md` in the current directory — get the list of active projects and their paths.
2. For each active project, read (silently, without announcing each read):
   - `CONTEXT.md` — current state, decisions, blockers
   - `agent_loop/loop_state.md` — current objective, iteration, blockers
   - `agent_loop/spend.log` — compute cumulative spend from JSONL (sum `cost_usd` fields)
3. Produce a prioritised attention table:

| Project | Lifecycle | Spend / Budget | Last Activity | Priority | Action Needed |
|---------|-----------|----------------|---------------|----------|---------------|

Priority order (highest first):
- **BLOCKED** — loop_state.md shows blocker
- **Budget > 80%** — cumulative spend exceeds 80% of BUDGET_USD
- **Stale > 7 days** — no CONTEXT.md update in > 7 days (check last-modified or internal dates)
- **Lifecycle drift** — MAINTENANCE/ARCHIVED project with pending tasks
- **Active build** — normal active work, no flags

4. End with one sentence: which single project needs attention most and why.

No external API calls. Pure file reads only. Be terse — one table plus one sentence.
