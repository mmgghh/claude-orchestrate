# claude-orchestrate

A Claude Code plugin for running big, multi-stage plans without burning through your usage limits.

It turns your main session into a **thin orchestrator**: the plan lives in a file, tasks go to small focused workers that report back in a few lines, and Claude tells you when it's a good moment to `/clear`. A hook also warns you when your session's context grows past about 150k tokens.

## Install

In Claude Code:

```
/plugin marketplace add mmgghh/claude-orchestrate
/plugin install orchestrate@claude-orchestrate
```

To try it without installing: `claude --plugin-dir ./plugins/orchestrate`

## Use

1. Write your plan in plan mode and save it as a checklist, for example `docs/plan.md`:

   ```markdown
   ## Stage 1 — <goal>
   - [ ] 1.A1 <task> · files: <paths> · test: <command>
   - [ ] 1.A2 <task> · depends on 1.A1
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

## What it does (and doesn't)

The skill is plain Markdown. The hook is one short Python script that runs locally: it reads only the token counts in your session transcript, makes no network calls, and writes a tiny state file to your system temp folder. It never sends or stores your conversation.

## Settings

Change when the hook warns you by adding these to the `env` block of `~/.claude/settings.json`:

| Variable | Default | Meaning |
| --- | --- | --- |
| `CLEAR_REMIND_AT` | `150000` | Context size, in tokens, for the first reminder |
| `CLEAR_REMIND_STEP` | `40000` | How many more tokens before the next reminder |

The hook needs `python3` on your PATH.

## How it differs from similar tools

This plugin is deliberately small: one ~500-word skill and one hook, with no review stages, agents or dependencies. If you want something heavier or different, these are worth a look:

| Project | Pick it when you want |
| --- | --- |
| [superpowers](https://github.com/obra/superpowers) (`subagent-driven-development`, `executing-plans`) | A full engineering workflow with a fresh subagent per task and review stages |
| [Orchestra](https://github.com/carloluisito/orchestra) | Task decomposition into a dependency graph with focused sub-agents |
| [agent-handoff](https://github.com/willowryu/agent-handoff) | A strict plan → execute → verify flow with disk-backed state |
| [Wave Planning](https://github.com/arunprakashg/wave-planning) | Parallel execution of dependency-ordered waves in git worktrees |
| [Cache Guard](https://github.com/agulhas-labs/claude-plugins) | Cost warnings when a big context's prompt cache has expired, plus a handoff file |
| [ThinWindow](https://github.com/thinwindow/thinwindow) | Trimming oversized reads and logs to keep the window thin |

## Support

Questions, bugs and security concerns: [open an issue](https://github.com/mmgghh/claude-orchestrate/issues).

## License

MIT
