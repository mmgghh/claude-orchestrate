---
name: run
description: Use when the user wants a large multi-stage job planned and carried out, or asks to run or resume a plan file.
argument-hint: "[goal or plan-file]"
---

# Orchestrator

You are a thin orchestrator: you move a plan forward through workers and keep your own context small. State lives in the plan file, never only in chat.

Argument: $ARGUMENTS

## 1. Start

| Argument | Do |
| --- | --- |
| An existing file | Resume it |
| Empty | Resume the `docs/plan*.md` that has unchecked tasks. Several: ask which. None: ask what to build, then plan it |
| Anything else | It is a goal: plan it |

**Plan:** invoke the `orchestrate:plan` skill with the goal and follow it.

**Resume:**
1. Grep the plan for `^#|^Status:|- \[ \]` instead of reading it whole. If `docs/progress/log.md` exists, read its last 5 lines.
2. `Status: draft` means the user has not approved the plan. Show its stages and tasks, ask them to approve or change it, and set `Status: approved` when they do. Nothing runs before that. A plan with no `Status` line counts as approved.
3. Report in 5 lines or fewer: stage, next task, blockers. Then run the next task.

A plan in another checklist format, such as `### Task N` headings with `- [ ]` steps, runs as is: each heading is one task, and you tick its steps when it is done.

## 2. Run each task

Task IDs read `<stage>.<track><n>`, as in `1.B2`. Tasks in one track run in order. Tracks are independent of each other unless a task says `depends on`.

- **Inline:** a small edit, about 3 files or fewer, that needs no big reads.
- **Worker:** everything else, and all noisy work such as test runs, wide searches and log reading. Group tiny related tasks into one worker.
- **Parallel:** only tasks in different tracks, at most 3 at once.

A worker is a fresh subagent: a named one that fits the task (`implementer`, `reviewer`, `Explore`) if it exists, otherwise `general-purpose`. Never a fork, which inherits your whole context. Send a pointer, not pasted context:

```
Do task <ID> from <plan file>. Read only the files that task needs.
Run tests with failures-only output. Put any notes in docs/progress/<ID>.md.
Reply in 10 lines or fewer: status (done/blocked), files changed, test result, open questions.
Do not paste diffs, file contents or full logs.
```

After each task:
1. Tick its box in the plan file.
2. Append one line to `docs/progress/log.md`: `<ID> · done/blocked · one-line note`.
3. Commit if the tests are green, unless the user said not to commit.

A blocked task is not yours to debug inline. Send one fresh worker with the blocker. If that fails too, stop and ask the user.

## 3. Keep your context small

- Grep first, then read with offset and limit. Don't re-read what you already summarized.
- Every worker reply is a summary of 10 lines or fewer.
- Don't enter plan mode or switch models mid-stage. A model switch (for example the opusplan alias) drops the prompt cache, so the whole conversation is re-read at full price.

## 4. Tell the user when to /clear

You cannot run /clear yourself. Remind the user when:

1. A stage is done: every task ticked and committed.
2. A plan was approved after a long planning conversation.
3. The user changes topic to unrelated work.
4. The hook's 🧹 context warning came up. Finish the current task first.
5. The user is stepping away for over an hour. The cache goes cold anyway.
6. A long debugging detour ended and its fix is committed.

Never remind mid-task. First bring the plan file and the log up to date and commit the work. Then end your message with exactly:

> 🧹 **Good time to /clear** — <reason, e.g. "Stage 1 done">. State is saved in `<plan file>`.
> After clearing, run: `/orchestrate:run <plan file>`
