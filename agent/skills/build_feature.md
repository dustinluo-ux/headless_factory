# Skill: build_feature

> Use when asked to implement a new feature or behaviour.

---

## Trigger

"add X", "implement X", "build X", "I need X to do Y"

---

## Workflow

### 1. Understand
- Restate the requirement in one sentence. If you can't, ask one clarifying question.
- Identify which files will be touched (read them before writing anything).
- Check `SPEC.md` if it exists — requirement must be consistent with scope.

### 2. Locate
- Find the right layer: logic → `src/`, runner → `scripts/`, config → root or `agent/`.
- Check for existing functions that already do part of this. Extend before adding.

### 3. Implement
- Write the minimal working version first. No future-proofing yet.
- Follow `agent/rules.yaml`: max 30 lines/function, max depth 3, snake_case.
- If touching money or external state, add explicit error handling.

### 4. Test
- Add or update tests in `tests/` for every new function that touches I/O or state.
- Run tests before declaring done.
- At minimum: one happy-path test, one failure case.

### 5. Summarize
Report:
- Files changed and why
- What the feature does (one sentence)
- Any assumptions made
- Tests added

---

## Hard stops

- Do not write without reading relevant files first.
- Do not skip tests if the function touches external state.
- Do not add abstractions unless 3+ call sites would benefit.
