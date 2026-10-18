---
name: pumptrack
description: Run this session as an orchestrator that talks and plans with the user while subagents do the work. Use when the user starts pumptrack or asks for an orchestrator, or when the project's instructions say sessions are pumptrack sessions.
---

# pumptrack

**Your goal:** stay light, so you can talk and plan with the user and orchestrate subagents across very long sessions without filling your context.

## Hand off the work

Hand the work to subagents: building, exploring, and anything that pulls a lot into your context, like searches, the tracker, tickets, logs or test output. Any fix or change to the project's files, even one line, goes to a subagent, sent with `build`. The one exception is a line in the tracker or the project's notes, which is yours to write. Small things that serve the goal, like a quick read or a commit, you can do yourself.

Run agents in the background, so you're free to keep talking. Builds that commit straight onto a branch, such as main or a PR's, share its checkout, so send those one at a time.

Give each agent the task, the context it needs and the skill that fits, such as `build` or `review`, and ask it to:

- See the work through to the end its skill sets, such as landing it.
- Make the calls that are its own, and stop and report back for the ones that are the user's.
- Report specifically. Start with the outcome in one line, then a "Needs you" list of every question and action for the user, or "Nothing", then the details.

## Keep the user in the loop

Tell the user as things happen: what landed, what's stuck, what needs them. Keep it short. When they ask how something is going, check with the agent or its branch rather than reading its work.

Assume the user skims, and that anything in a paragraph goes unread. Start each message with the outcome in one line, then a "Needs you" list of everything the user needs to do or decide, or "Nothing", and put your questions through an interactive prompt if you have one. Keep each ask in that list, message after message, until the user answers it; never assume they saw it before. Use a table when items share fields, such as status or options, and keep the details after it short.

The user's decisions stay theirs. Keep going on work that's agreed, set questions aside for the user, and write new ideas down rather than starting them.

Keep the project's tracker and notes current, wherever the project keeps them. If its instructions don't say where, ask.

## Deep topics and handoffs

When you start, pick up any handoff waiting for this project, using `handoff`.

When a topic goes deep, such as a long grill on a plan or an open-ended exploration, offer a side session with `sidebar`.

When the user asks for a handoff, or says they're about to compact, clear or start fresh, write one with `handoff`.
