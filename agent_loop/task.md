# task.md — Headless Factory Upgrade: Agent Teams + gstack Planning Skills

**Task ID**: 002
**Created**: 2026-03-24
**Status**: PLAN — approved before Cursor implementation

---

## Objective

Upgrade `templates/CLAUDE.md.template` with two additive layers — Native Agent Teams (Researcher + Auditor)
and gstack Planning Skills references — plus create an optional AutoResearch R&D Pod template, without
modifying any existing workflow, governance, or agent_loop structure.

---

## Scope Review

### What was reviewed
- `templates/CLAUDE.md.template` — current structure: 6 sections, ~63 lines
- `templates/SKILL.md.template` — universal patterns (atomic write, logger, kill switch, Decimal)
- `templates/agent_loop/task.md.template` — Claude→Cursor handoff format (unchanged)
- `templates/agent_loop/loop_state.md.template` — iteration snapshot (unchanged)
- `MASTER_RULES.md` — § 1–5 constitution (unchanged)
- `identity.md` — Valuation SME persona + 5 Hard Limits (source for Auditor)
- `agent/skills/` — 6 skills: write_task, build_feature, refactor_safe, repo_map, test_generator, bug_hunt (unchanged)
- `~/.claude/skills/gstack/` — 27 skills globally installed, SKILL.md files freshly regenerated

### Decision: gstack inclusion method
Gstack skills are globally installed at `~/.claude/skills/`. Claude Code loads them automatically.
No copying needed. The only addition required is a reference table in CLAUDE.md.template so
bootstrapped projects know to use them at the right phases.
**Rationale**: Copying would create maintenance burden; reference is zero-maintenance and defers to
gstack's own regenerated SKILL.md for the actual instructions.

### Decision: AutoResearch R&D Pod
Implemented as `templates/research/r_and_d_pod.md.template` only. Not injected automatically.
Bootstrap procedure does NOT create it by default — user opts in by copying it to `research/`.
**Rationale**: Keeps bootstrap output minimal; power users who need structured research workflows
can activate it explicitly.

---

## Files to Modify

| File | Change |
|------|--------|
| `templates/CLAUDE.md.template` | Add §§ "Agent Teams" and "Planning Skills" after existing "Workflow" section |

## Files to Create

| File | Purpose |
|------|---------|
| `templates/research/r_and_d_pod.md.template` | Optional AutoResearch R&D Pod template |

## Files NOT modified (explicitly preserved)
- `MASTER_RULES.md`
- `identity.md`
- `templates/SKILL.md.template`
- `templates/agent_loop/*.md.template`
- `templates/SPEC.md.template`
- `templates/CONTEXT.md.template`
- `agent/skills/*`
- `CLAUDE.md` (this repo's own instructions)

---

## Planned Diffs

### templates/CLAUDE.md.template — insert after line 49 (end of "## Workflow" section)

```diff
+---
+
+## Agent Teams
+
+Two sub-agent roles available via the `Agent` tool. Invoke explicitly at the phases below.
+
+### Researcher
+**Trigger**: Any task requiring external facts — market data, competitor analysis, literature review,
+prior art, regulatory lookups.
+**Subagent instructions**:
+- Gather and cite; do not fabricate sources.
+- Write structured findings to `research/[topic]-[YYYY-MM-DD].md` with: source URL, retrieval date,
+  confidence level (HIGH = primary source / MEDIUM = secondary / LOW = inferred).
+- Return a one-paragraph summary to the calling agent with key facts and confidence assessment.
+
+### Auditor
+**Trigger**: Automatically before finalising any `project_plan.md`, and before any irreversible
+external action (API call, git push, database write, external service call).
+**Subagent instructions**: Read `.constitution/identity.md` § Hard Limits. The plan **PASSES** only
+if ALL five hold:
+1. Risk register present and bear case is the anchor (not the base case)
+2. No float for monetary calculations anywhere in scope — Decimal confirmed
+3. Every valuation/analytical output states methodology and assumptions explicitly
+4. API spend tracked; no call exceeds remaining `BUDGET_USD` without user confirmation
+5. No output range is too wide to be decision-relevant
+
+**Output**: `PASS — [evidence for each of the 5]` or `BLOCK — [specific violation(s)]`.
+A `BLOCK` halts execution immediately. Do not proceed past a BLOCK without resolving the violation.
+
+---
+
+## Planning Skills
+
+If gstack is installed (`~/.claude/skills/gstack/` exists), invoke these skills at the named phases.
+All are optional but strongly recommended — especially `/plan-eng-review` before any Cursor handoff.
+
+| Skill | Phase | When to use |
+|-------|-------|-------------|
+| `/office-hours` | Before writing `SPEC.md` | Expose demand reality, narrow scope, surface hidden assumptions |
+| `/plan-ceo-review` | After first plan draft | Strategic review — scope expansion or reduction, rethink premises |
+| `/plan-eng-review` | Before first Cursor task | Lock in architecture, data flow, edge cases, test coverage |
+| `/retro` | End of sprint / week | Commit history analysis, per-person breakdown, trend tracking |
+
+Check gstack is available:
+```bash
+ls ~/.claude/skills/gstack/SKILL.md 2>/dev/null && echo "gstack: installed" || echo "gstack: not found"
+```
+
+---
```

---

## Uncertainties and flags

1. **Auditor as mandatory vs. recommended**: The Auditor is described as "automatic" but Claude Code
   has no hook to force pre-plan checks. In practice, the CLAUDE.md.template instruction tells Claude
   to invoke Auditor before plans — it relies on Claude following instructions, not on a hard technical
   gate. This is the same model as the existing "Plan-Before-Act" rule. **Accepted tradeoff.**

2. **Auditor Hard Limits are Valuation SME specific**: Hard Limits 1, 3, 5 are valuation-specific
   (risk register, methodology, range relevance). For non-valuation projects these checks are less
   meaningful, but they still apply discipline (risk register = dependency/failure risk, methodology =
   documented approach, range = don't give vague estimates). **Accepted — the persona applies globally.**

3. **gstack availability check**: Bootstrapped projects have no guarantee gstack is installed.
   The template references `~/.claude/skills/gstack/` but cannot enforce installation. The bash
   check above makes it visible. **Accepted — reference only, no hard dependency.**

4. **R&D Pod template scope**: Kept to a structured Researcher invocation template. Does not
   include scheduling, cost tracking per research run, or persistence beyond flat .md files.
   Future extension point. **Accepted for now.**

---

## Acceptance Criteria

- [ ] `templates/CLAUDE.md.template` gains "Agent Teams" and "Planning Skills" sections
- [ ] No existing section modified or removed
- [ ] Auditor section references all 5 identity.md Hard Limits explicitly
- [ ] gstack skill table maps all 4 named skills to correct phases
- [ ] `templates/research/r_and_d_pod.md.template` created and self-contained
- [ ] `agent_loop/task.md` (this file) reflects the approved plan
- [ ] All token substitution variables (`{{...}}`) preserved and unbroken

---

## Implementation notes

Implementation is performed directly by Claude Code (not a Cursor handoff) because the changes
are pure template text additions with no logic, no new dependencies, and no tests required.
Cursor task generation not needed for this task.
