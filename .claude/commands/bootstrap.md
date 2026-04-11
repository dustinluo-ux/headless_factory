Bootstrap a new project using the Headless Factory procedure.

Read `CLAUDE.md` in this repo (headless_factory) to get the full bootstrap procedure.

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

Once all required fields are known, execute the full bootstrap procedure (Steps 1–8 in CLAUDE.md) without further prompting. Report completion with the checklist from Step 8.
