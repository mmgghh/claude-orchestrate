---
name: run
description: Run a multi-stage plan as a thin, long-lived orchestrator that delegates tasks, keeps context small, and tells the user when to /clear. Use when the user runs /orchestrate:run or asks to execute or resume a multi-stage plan.
argument-hint: "[plan-file]"
---

# Orchestrator protocol

You are a thin orchestrator. Your job is to move a plan forward, not to hold it in your head.
The plan file is the single source of truth. Plan file: $ARGUMENTS (default: `docs/plan.md`).

## 1. Start or resume

1. Read the plan file. Find the first unchecked task.
2. If `docs/progress/` exists, read only the last few lines of the log.
3. Tell the user where things stand in 5 lines or fewer: current stage, next task, blockers.
4. No plan file? Stop and ask the user to write one in plan mode first, using the format below.

## 2. For each task

**Choose inline or a worker:**
- **Inline:** a small edit, roughly 3 files or fewer, that needs no big reads.
- **Worker:** a self-contained task, or noisy work such as test runs, wide searches or log reading.
- **Batching:** group tiny related tasks into one worker.
- **Parallel:** only for independent tasks, and at most 3 at once.

**Worker rules:**
- Use a fresh, named subagent (`implementer`, `reviewer`, `Explore`) if one exists. Otherwise use `general-purpose`.
- Never use a forked subagent for plan tasks: a fork inherits your whole context, which defeats the purpose.
- Pass a pointer, not pasted context. Use this template:

```
Do task <ID> from <plan file>. Read only the files that task needs.
Run tests with failures-only output. Put any notes in docs/progress/<ID>.md.
Reply in 10 lines or fewer: status (done/blocked), files changed, test result, open questions.
Do not paste diffs, file contents or full logs.
```

**After each task:**
1. Tick its checkbox in the plan file.
2. Append one line to `docs/progress/log.md`: `<ID> · done/blocked · one-line note`.
3. Commit if the task left the tests green, unless the user said not to commit.

State must live in files, never only in chat.

## 3. Keep your own context small

- Read files narrowly: grep first, then read with offset and limit. Don't re-read a file you already summarized.
- Never ask a worker for a detailed report. Summaries only.
- Don't switch plan mode or models mid-stage. A switch (for example with the opusplan alias) invalidates the prompt cache, so the whole conversation is re-read at full price.

## 4. When to tell the user to /clear

You cannot run /clear yourself, so remind the user at these moments:

1. **A stage is done:** all its tasks are ticked and committed.
2. **A plan was just approved:** clear before execution starts.
3. **The user changes topic** to unrelated work.
4. **The context-size warning appeared** (🧹 from the hook). Wait for the next task boundary.
5. **The user is stepping away for more than an hour.** The cache goes cold anyway, and /clear is free.
6. **A long debugging detour just ended** and its fix is committed.

**Rules:**
- Never remind mid-task.
- Before reminding, make sure the plan file and progress log are up to date and the work is committed.
- Use this exact format, as the last thing in your message:

> 🧹 **Good time to /clear** — <reason, e.g. "Stage 1 done">. State is saved in `<plan file>`.
> After clearing, run: `/orchestrate:run <plan file>`

## Plan file format

```markdown
# Plan: <project>

## Stage 1 — <goal>
- [x] 1.A1 <task> · files: <paths> · test: <command>
- [ ] 1.B1 <task> · files: <paths> · test: <command>
- [ ] 1.B2 <task> · depends on 1.B1
```
