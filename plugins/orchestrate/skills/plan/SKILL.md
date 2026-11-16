---
name: plan
description: Use when the orchestrate:run skill needs a plan written for a new goal.
argument-hint: "[goal]"
user-invocable: false
---

# Planning a new goal

You write the plan and the user approves it in step 5. Nothing runs before that, and no earlier reply counts as approval.

Goal: $ARGUMENTS

1. **Look.** List the top-level files and read the first 40 lines of the README. Leave deeper exploring to the planner.

2. **Ask once.** Send one message in this shape, then wait. Do this even when you have no questions: leave out the Questions block, and the user still gets to add their notes.

   ```
   **Goal as I understand it:** <one or two lines>

   **Questions** (answer by number, or skip one to take my recommendation)
   1. <question>? Recommended: <your pick>

   **Anything else?** Write freely: what you are after, constraints, preferences, things to avoid.
   Or reply `go` to accept all my recommendations. Either way, I will show you the plan to approve before anything runs.
   ```

   The reply to this message, `go` included, is input for the plan and never approval of it. Ask as few questions as the plan needs, and never more than 10. Ask a question only if it is something only the user can answer and a wrong guess would noticeably hurt the plan: scope, priorities, constraints, risky or hard-to-reverse choices. The more a question affects the quality of the plan, the more it is worth asking. Do not ask about details you can decide yourself or the planner can find in the code. Every question carries a concrete recommendation, so replying `go` is always a good answer. Put the questions that matter most first.

3. **Save the brief.** Create `docs/orchestrate/plan.md`, or `docs/orchestrate/plan-<slug>.md` if that file exists:

   ```markdown
   # Plan: <project>

   Status: draft

   ## Brief
   Goal: <one or two lines>
   Answers: <each answer, or the default taken>
   Notes: "<the user's free text, word for word>"
   ```

4. **Write the stages.** If the goal fits in about 5 tasks and needs no exploring, add them yourself in the format below. Otherwise send a fresh `general-purpose` worker, because the planner must be able to write the file:

   ```
   Fill in the stages of <plan file>. Its Brief holds the goal and the user's notes: follow them.
   Explore the repo only as far as the plan needs. Leave the Brief as it is and add below it:
   ## Stage N — <goal>
   - [ ] N.A1 <task> · files: <paths> · test: <command>
   - [ ] N.A2 <task> · files: <paths> · test: <command>
   - [ ] N.B1 <task> · depends on N.A1
   IDs are <stage>.<track><n>. Tasks in one track run in order. Tracks are independent of each other
   unless a task says "depends on", so put work that can run in parallel in separate tracks.
   Each task is one sitting of work for one worker, and names its files and how to check it.
   Each stage ends with something that works and is tested.
   Reply in 10 lines or fewer: stage titles with task counts, assumptions you made, open questions.
   Do not paste the plan.
   ```

5. **Review.** Show the user the plan file path, each stage with its tasks one line each (only stage titles and task counts if there are more than 30 tasks), and the assumptions and open questions. End with:

   > Reply `approve` to run one stage at a time: I stop after each stage so you can check it and /clear.
   > Reply `approve auto` to run every stage without stopping: each stage runs in its own fresh subagent, and I stop only if one is blocked.
   > Or tell me what to change, or edit the file yourself and then approve.

   Then wait. Approval is the user's reply to this review message. For changes, make them (send large ones back to a worker), say what changed, and ask again. If the user edited the file, grep it again. On approval, set `Status: approved` and write the mode on the line below it: `Mode: auto` if they chose auto, otherwise `Mode: manual`.

6. **Clear or continue.** If planning took more than one round of questions or changes, or this session held other work before the plan, end your message with exactly:

   > 🧹 **Good time to /clear** — plan approved. State is saved in `<plan file>`.
   > After clearing, run: `/orchestrate:run <plan file>`

   Otherwise start Stage 1 now under the `orchestrate:run` skill, in the mode the user chose. Invoke it with the plan file if it is not loaded yet.
