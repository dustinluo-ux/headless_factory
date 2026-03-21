# Skill: bug_hunt

> Use to investigate a failure, unexpected behaviour, or suspected defect.

---

## Trigger

"something's broken", "this fails with X", "unexpected output", "investigate Y", "why does Z happen"

---

## Workflow

### 1. Reproduce
- Get the exact failure: error message, stack trace, or wrong output.
- Identify the minimal input that triggers it.
- If it's intermittent, note what varies (timing, input shape, env).

### 2. Trace
- Start at the failure point (error line or wrong-output line).
- Walk backwards: what called this? what was the input? where did that come from?
- Read the actual code — do not guess from function names alone.

### 3. Hypothesize
State the hypothesis explicitly:
> "I think the bug is in `[file]:[line]` because `[reason]`."

Check the hypothesis against the code before proposing a fix.

### 4. Identify root cause
Distinguish:
- **Symptom**: where it fails (the error line)
- **Root cause**: why it fails (the actual defect)
- **Contributing condition**: what makes it happen now but not always

Fix the root cause, not the symptom.

### 5. Propose fix
- Write the minimal change that fixes the root cause.
- Do not refactor or improve surrounding code during a bug fix.
- Add a regression test that would have caught this bug.

### 6. Report
```
BUG: [one-line description]
SYMPTOM: [what the user observed]
ROOT CAUSE: [file:line — what was actually wrong]
FIX: [what was changed]
REGRESSION TEST: [test added to prevent recurrence]
```

---

## Hard stops

- Do not fix symptoms — trace to root cause first.
- Do not refactor during a bug fix — one change, one purpose.
- Do not close the bug without a regression test.
