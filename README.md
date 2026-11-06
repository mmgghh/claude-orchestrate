# claude-orchestrate

A Claude Code plugin for running big, multi-stage plans without burning through your usage limits.

It turns your main session into a **thin orchestrator**: the plan lives in a file, tasks go to small focused workers that report back in a few lines, and Claude tells you when it's a good moment to `/clear`. A hook also warns you when your session's context grows past about 150k tokens.

## Install

In Claude Code:

```
/plugin marketplace add <your-github-user>/claude-orchestrate
/plugin install orchestrate@claude-orchestrate
```

## Use

1. Write your plan in plan mode and save it as a checklist, for example `docs/plan.md`:

   ```markdown
   ## Stage 6 — <goal>
   - [ ] 6.C1 <task> · files: <paths> · test: <command>
   - [ ] 6.C2 <task> · depends on 6.C1
   ```

2. Start or resume the orchestrator:

   ```
   /orchestrate:run docs/plan.md
   ```

3. When you see **🧹 Good time to /clear**, run `/clear`, then `/orchestrate:run docs/plan.md` again. Progress is saved in the plan file, so nothing is lost.

## What's inside

| Part | What it does |
| --- | --- |
| `skills/run` | The orchestrator protocol: delegate with pointers instead of pasted context, keep worker replies short, save state to files, and remind you to `/clear` at stage boundaries, topic changes, and breaks |
| `hooks/clear-reminder.py` | A `Stop` hook that reads the session's real context size and shows a 🧹 warning past 150k tokens, then every 40k after that. It goes quiet after you clear |

## Settings

Change when the hook warns you by adding these to the `env` block of `~/.claude/settings.json`:

| Variable | Default | Meaning |
| --- | --- | --- |
| `CLEAR_REMIND_AT` | `150000` | Context size, in tokens, for the first reminder |
| `CLEAR_REMIND_STEP` | `40000` | How many more tokens before the next reminder |

The hook needs `python3` on your PATH.

## License

MIT
