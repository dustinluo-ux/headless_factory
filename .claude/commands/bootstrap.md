# intentionally not delegating to scaffold — factory-specific
# scaffold_project.py creates a generic .claude/ guardrail stack for any project.
# Factory bootstrap creates 14+ files/dirs from domain-specific templates,
# constitution files, Cursor config, research scaffolding, and consult scripts.
# These are different scopes; the factory procedure is not a subset of scaffold.

Bootstrap a new project using the Headless Factory procedure.

Collect the following fields — ask for all missing required ones in a single message (never one at a time):

| Field | Required | Default |
|-------|----------|---------|
| `name` | Yes | — |
| `purpose` | Yes | — |
| `target_dir` | Yes | ask |
| `github` | Yes | ask (private / public / none) |
| `skills` | No | none |
| `budget` | No | 5.00 |

If purpose is obvious from context, infer it and confirm rather than asking.

Once all required fields are known, execute the full 8-step procedure in
`.claude/commands/bootstrap-procedure.md` without further prompting.
Report completion with the checklist from Step 8.
