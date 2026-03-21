# Skill: write_task

> Use when Claude is writing the next task for Cursor to implement.
> The goal: give Cursor exactly what it needs — nothing more.

---

## Trigger

"write a task for", "next task", "create task for Cursor", "hand off to Cursor"

---

## Constraint Before Starting

Read `repo_context.md` first. If it does not exist or is stale, run `repo_map` skill first.
Do NOT write a task that requires Cursor to read files you haven't explicitly listed.

---

## Workflow

### 1. Define the objective
Write one sentence: what must be true when this task is complete?
If you need more than one sentence, split into two tasks.

### 2. Identify the minimal file set
List the exact files Cursor needs to read. Ask:
- Does Cursor need SPEC.md? (usually no — extract the relevant constraint into the task)
- Does Cursor need CONTEXT.md? (never — put relevant state in the task directly)
- Does Cursor need SKILL.md? (only if implementing a domain-specific pattern)

Default file set: `repo_context.md` + the specific `src/` files being changed.

### 3. List files to modify
Explicit list only. If you are not certain a file needs to change, leave it off.
Cursor must not modify unlisted files. If it needs to, it should flag and stop.

### 4. Write acceptance criteria
Each criterion must be:
- Binary (pass/fail, not "should look reasonable")
- Independently checkable (a command, not a judgment)
- Specific to this task (not generic rules)

### 5. Write the validation command
The exact CLI command Cursor (or the developer) runs to confirm the task is done.
If there is no automated check, state the exact manual check.

### 6. Set constraints
List what Cursor must NOT do:
- Refactor unrelated code
- Add dependencies
- Modify files outside the list
- Add task-specific limits (e.g., "do not change the model architecture")

### 7. Write to `agent_loop/task.md`
Overwrite — do not append. One active task at a time.
Update `agent_loop/loop_state.md` with the new task ID and objective.

---

## Quality Check (before finalizing)

- [ ] Objective is one sentence
- [ ] File list is minimal (< 5 files unless truly necessary)
- [ ] Every acceptance criterion has an automated check
- [ ] Validation command is runnable right now
- [ ] No "read the whole repo" instructions

---

## Hard Stops

- Do not write a task that requires reading CONTEXT.md, SPEC.md, or SKILL.md unless those
  files contain something Cursor literally cannot implement without (e.g., domain formula).
- Do not write a task with vague acceptance criteria ("should work", "looks correct").
- Do not write multiple objectives in one task — split them.
