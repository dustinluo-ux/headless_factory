# Skill: test_generator

> Use to create or expand test coverage for existing code.

---

## Trigger

"write tests for X", "add tests", "test coverage", "what's untested"

---

## Workflow

### 1. Read the code
- Read the target function/module in full before writing any tests.
- Identify: inputs, outputs, side effects, error conditions.
- Check if tests already exist — extend, don't duplicate.

### 2. Classify test cases
For each function, identify:

| Case | Description |
|------|-------------|
| Happy path | Valid input, expected output |
| Boundary | Edge of valid range (empty list, zero, max value) |
| Bad input | Invalid type, missing required field, null |
| Failure path | What happens when a dependency fails (I/O error, bad API response) |

Write at least happy path + one failure case per function.

### 3. Write tests
- One test function per case. Name it `test_[function]_[case]`.
- Keep each test under 20 lines.
- Avoid mocking unless the dependency is truly external (network, filesystem).
- Prefer real objects over mocks wherever possible.
- For filesystem tests: use `tmp_path` (pytest) or `tempfile`.

### 4. Run and fix
- Run the tests. Fix failures before reporting.
- A test that always passes is worthless — verify it actually catches the failure case.

### 5. Report
- List functions tested
- List cases covered per function
- Flag any untestable code (and why)

---

## Hard stops

- Do not mock internal modules — only external I/O.
- Do not write tests that pass regardless of implementation correctness.
- Do not skip edge cases for "simple" functions — they're where bugs hide.
