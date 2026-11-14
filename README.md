# claude-orchestrate

A Claude Code plugin for running big, multi-stage plans without burning through your usage limits.

It turns your main session into a **thin orchestrator**: Claude writes the plan for you to approve, the plan lives in a file, tasks go to small focused workers that report back in a few lines, and Claude tells you when it's a good moment to `/clear`. A hook also warns you when your session's context grows past about 150k tokens.

## Install

In Claude Code:

```
/plugin marketplace add mmgghh/claude-orchestrate
/plugin install orchestrate@claude-orchestrate
```

To try it without installing: `claude --plugin-dir ./plugins/orchestrate`

## Use

1. Say what you want:

   ```
   /orchestrate:run add CSV export to the reports page
   ```

2. Answer the intake message. Claude asks only the questions the plan needs (up to ten, fewer when it can), each with a recommended answer, and invites you to write anything else freely: your intent, constraints, things to avoid. Answer by number, or reply `go` to accept all the recommendations.

3. Review the plan. Claude writes it to `docs/plan.md` and shows you the stages and tasks. Reply `approve`, ask for changes, or edit the file yourself and then approve. Nothing is executed before you approve.

4. When you see **🧹 Good time to /clear**, run `/clear`, then `/orchestrate:run` again. Progress is saved in the plan file, so nothing is lost.

To resume later, run `/orchestrate:run` with no argument, or pass the plan file: `/orchestrate:run docs/plan-export.md`.

### Bring your own plan

You can also write the plan yourself and pass its path. The format is a checklist:

```markdown
## Stage 1 — <goal>
- [ ] 1.A1 <task> · files: <paths> · test: <command>
- [ ] 1.A2 <task> · depends on 1.A1
```

Plans in other checklist formats work too, for example a superpowers plan with `### Task N` headings and `- [ ]` steps.

## What's inside

| Part | What it does |
| --- | --- |
| `skills/run` | The orchestrator protocol: delegate with pointers instead of pasted context, keep worker replies short, save state to files, and remind you to `/clear` at stage boundaries, topic changes, and breaks |
| `skills/plan` | The planning steps: ask you once, save your notes as a brief, write the plan, and wait for your approval. `run` loads it only when you give it a new goal, so resuming a plan stays cheap |
| `hooks/clear-reminder.py` | A `Stop` hook that reads the session's real context size and shows a 🧹 warning past 150k tokens, then every 40k after that. It goes quiet after you clear |

## What it does (and doesn't)

The skills are plain Markdown. The hook is one short Python script that runs locally: it reads only the token counts in your session transcript, makes no network calls, and writes a tiny state file to your system temp folder. It never sends or stores your conversation.

## Settings

Change when the hook warns you by adding these to the `env` block of `~/.claude/settings.json`:

| Variable | Default | Meaning |
| --- | --- | --- |
| `CLEAR_REMIND_AT` | `150000` | Context size, in tokens, for the first reminder |
| `CLEAR_REMIND_STEP` | `40000` | How many more tokens before the next reminder |

The hook needs `python3` on your PATH.

## How it differs from similar tools

This plugin is deliberately small: two short skills and one hook, with no review stages, agents or dependencies. If you want something heavier or different, these are worth a look:

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
