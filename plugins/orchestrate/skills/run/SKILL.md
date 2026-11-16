---
name: run
description: Use when the user wants a large multi-stage job planned and carried out, or asks to run or resume a plan file.
argument-hint: "[goal or plan-file]"
---

# Orchestrator

You are a thin orchestrator: you move a plan forward through workers and keep your own context small. State lives in the plan file, never only in chat.

Argument: $ARGUMENTS

If your prompt says you are a stage runner, follow **Stage runners** in section 3 instead of section 1.

## 1. Start

| Argument | Do |
| --- | --- |
| An existing file | Resume it |
| Empty | Resume the `docs/orchestrate/plan*.md` that has unchecked tasks. Several: ask which. None: ask what to build, then plan it |
| Anything else | It is a goal: plan it |

**Plan:** invoke the `orchestrate:plan` skill with the goal as your first action, before you look at any file, then follow it.

**Resume:**
1. Read the plan's `## Brief` at the top of the file, if it has one: it holds the user's constraints. Grep the rest for `^#|^Status:|^Mode:|- \[ \]` instead of reading it whole. If `docs/orchestrate/progress/log.md` exists, read its last 5 lines.
2. `Status: draft` means the user has not approved the plan. Show its stages and tasks, and ask them to reply `approve` (one stage at a time), `approve auto` (every stage without stopping), or what to change. When they approve, set `Status: approved` and write `Mode: manual` or `Mode: auto` on the line below it. Nothing runs before that. A plan with no `Status` line counts as approved.
3. Report in 5 lines or fewer: stage, mode, next task, blockers. Then carry on in the plan's mode.

**Mode:** the plan's `Mode` line says how far you go.

| Mode line | Do |
| --- | --- |
| `Mode: manual`, or none | Run one stage yourself, then stop (section 2) |
| `Mode: auto` | Run every stage through stage runners (section 3) |

If the user asks to switch, edit the line and carry on in the new mode.

A plan in another checklist format, such as `### Task N` headings with `- [ ]` steps, runs as is: each heading is one task, and you tick its steps when it is done. If it has no stages, the whole plan is one stage.

## 2. Run each task

Task IDs read `<stage>.<track><n>`, as in `1.B2`. Tasks in one track run in order. Tracks are independent of each other unless a task says `depends on`.

- **Inline:** a small edit, about 3 files or fewer, that needs no big reads.
- **Worker:** everything else, and all noisy work such as test runs, wide searches and log reading. Group tiny related tasks into one worker.
- **Parallel:** only tasks in different tracks, at most 3 at once.

A worker is a fresh subagent: a named one that fits the task (`implementer`, `reviewer`, `Explore`) if it exists, otherwise `general-purpose`. Never a fork, which inherits your whole context. Send a pointer, not pasted context:

```
Do task <ID> from <plan file>, within the constraints in its Brief. Read only the files that task needs.
Run tests with failures-only output. Put any notes in docs/orchestrate/progress/<ID>.md.
Leave the plan file, the log and committing to me.
Reply in 10 lines or fewer: status (done/blocked), files changed, test result, open questions.
Do not paste diffs, file contents or full logs.
```

After each task:
1. Tick its box in the plan file.
2. Append one line to `docs/orchestrate/progress/log.md`: `<ID> · done/blocked · one-line note`.
3. Commit if the tests are green, unless the user said not to commit. Stage only that task's files, by name: the tree may hold unfinished changes from a parallel worker or the user.

Stop at the end of each stage: post the reminder from section 5 instead of starting the next stage.

A blocked task is not yours to debug inline. Send one fresh worker with the blocker. If that fails too, stop and ask the user.

## 3. Auto mode

With `Mode: auto` you run no tasks yourself. Each stage goes to a stage runner: a fresh `general-purpose` subagent that runs that one stage in its own context, the way a new session would after /clear. Send one runner at a time, for the first stage that has unchecked tasks:

```
You are a stage runner. Invoke the `orchestrate:run` skill with `<plan file>` and run Stage <N> only.
Reply in 10 lines or fewer: tasks done, tasks blocked and why, test result, open questions.
```

When the runner replies, grep the plan again and look at that stage:

| Stage <N> has | Do |
| --- | --- |
| No unchecked tasks | Tell the user in one line, `Stage <N> done · <n> tasks · <test result>`, then send the runner for the next stage |
| Unchecked tasks, and the runner said blocked | Stop and bring the blocker to the user |
| Unchecked tasks for any other reason | Send one more fresh runner for the same stage. If that one leaves tasks unchecked too, stop and tell the user |

When the plan has no unchecked tasks left, say it is complete.

**Stage runners.** If you are one, you run a single stage and nothing else:
1. Do step 1 of Resume in section 1. Skip the report.
2. Run the unchecked tasks of your stage as section 2 says: you send the workers, tick the boxes, write the log and commit. Ignore the plan's `Mode` line, and never send a stage runner yourself.
3. You cannot reach the user. Where this skill says to ask the user, stop and reply `blocked` with the question instead.
4. When the stage is done, do not start the next one and do not post a /clear reminder. Send the reply your prompt asks for.

## 4. Keep your context small

- Grep first, then read with offset and limit. Don't re-read what you already summarized.
- Every worker reply is a summary of 10 lines or fewer.
- Don't enter plan mode or switch models mid-stage. A model switch (for example the opusplan alias) drops the prompt cache, so the whole conversation is re-read at full price.

## 5. Tell the user when to /clear

You cannot run /clear yourself. Remind the user when:

1. A stage is done in manual mode: every task ticked and committed. Auto mode needs no /clear between stages.
2. A plan was approved after a long planning conversation.
3. The user changes topic to unrelated work.
4. The user mentions the hook's 🧹 context warning, which is shown only to them. Finish the current task first.
5. The user is stepping away for over an hour. The cache goes cold anyway.
6. A long debugging detour ended and its fix is committed.

Never remind mid-task. First bring the plan file and the log up to date and commit the work. Then end your message with exactly:

> 🧹 **Good time to /clear** — <reason, e.g. "Stage 1 done">. State is saved in `<plan file>`.
> After clearing, run: `/orchestrate:run <plan file>`

If the plan has no unchecked tasks left, say it is complete and leave out the `After clearing` line.
