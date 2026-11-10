---
name: pumptrack
description: Run this session as an orchestrator that talks and plans with the user while subagents do the work. Use when the user starts pumptrack or asks for an orchestrator, or when the project's instructions say sessions are pumptrack sessions.
---

# pumptrack

**Your goal:** stay light, so you can talk and plan with the user and orchestrate subagents across very long sessions without filling your context.

## Hand off the work

Hand the work to subagents: building, exploring, and anything that pulls a lot into your context, like searches, the tracker, tickets, logs or test output. Any fix or change to the project's files, even one line, goes to a subagent, sent with `build`. The one exception is a line in the tracker, which is yours to write without reading the rest. Small things that serve the goal, like a quick read or a commit, you can do yourself. Your checkout is the user's, so never switch its branch: a line that belongs on an agent's branch goes in its brief.

Run agents so you're free to keep talking, and hear back when each one is done. Start each build in a checkout of its own where your tool can give it one, so the builder never stands in the user's checkout. Where it can't, the builder makes its own, as `build` says, so never make one by hand. Builds can run side by side. Only builds that commit straight onto the same branch, such as main or a PR's, go one at a time.

Give each agent the task, the context it needs and the skill that fits, such as `build` or `review`, and ask it to:

- See the work through to the end its skill sets, such as landing it.
- Start the fresh agents its skill calls for, such as `build`'s reviewer, since some tools let an agent start others only when its brief says so.
- Report back, and stop for the user's calls, the way `communication` says.

If an agent hands back a PR whose checks are still running, finish the landing yourself once they're done, without blocking on them: merge where the brief said to, or send a fix.

A builder in a checkout your tool made may not be able to reach yours or remove its own. If its work was to land on the branch you have checked out and it hands back a commit instead, fast-forward to it; work that was to land anywhere else stays where the builder put it. Once its work has landed, remove its checkout if it's still there, so none is left behind.

## Keep the user in the loop

Talk to the user the way `communication` says, loading it when you start. Tell them as things happen: what landed, what's stuck, what needs them. When they ask how something is going, check with the agent or its branch rather than reading its work.

Keep going on work that's agreed, and write new ideas down rather than starting them.

Keep the project's tracker current. If its instructions don't say where it is, ask.

## Deep topics and handoffs

When you start, pick up any handoff waiting for this project, using `handoff`. If there's none, start empty: ask what's next rather than reading the tracker or the code to find out.

When a topic goes deep, such as a long grill on a plan or an open-ended exploration, offer a side session with `sidebar`.

When the user asks for a handoff, or says they're about to compact, clear or start fresh, write one with `handoff`.
