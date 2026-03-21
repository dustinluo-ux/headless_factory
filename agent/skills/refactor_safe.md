# Skill: refactor_safe

> Use when improving structure, readability, or coupling — without changing behavior.

---

## Trigger

"refactor X", "clean up X", "this is messy", "too tightly coupled", "hard to read"

---

## Workflow

### 1. Identify the smell
Pick exactly ONE of:
- Function too long (> 30 lines) → extract sub-functions
- Nesting too deep (> 3 levels) → flatten with early returns
- Duplicated logic → extract shared function (only if 3+ call sites)
- Mixed concerns → split into separate functions/modules
- Unclear names → rename

Do not fix multiple smells in one pass. One change, one commit.

### 2. Check interfaces
- List every call site of the code being changed.
- Confirm the public interface (function signature, return type) will stay identical.
- If the interface must change, treat this as a breaking change — stop and discuss.

### 3. Refactor
- Make the single structural change.
- Do not add features or fix bugs during a refactor pass.
- Keep the diff minimal and legible.

### 4. Verify
- Run existing tests. All must pass — zero regressions allowed.
- If tests break, the refactor changed behaviour. Revert and reassess.

### 5. Summarize
Report:
- What smell was fixed
- Files changed
- Test result (pass/fail count)

---

## Hard stops

- Do not refactor and fix a bug in the same diff.
- Do not rename public interfaces without updating all call sites.
- Do not add abstraction layers unless behavior is already duplicated 3+ times.
