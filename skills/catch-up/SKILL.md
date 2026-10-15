---
name: catch-up
description: Bring the user back up to speed with one table of what needs them, what's done, what's in progress, what's waiting on others and what went wrong. Use when the user asks to catch up or where things stand, such as after time away, or when another session asks for a catch-up.
---

# Catch-up

**Your goal:** bring the user back up to speed in one table they can take in at a glance, built from what's true now rather than what you remember.

## What it covers

In a `pumptrack` session, cover the project. Anywhere else, cover this session's thread, such as a sidebar's topic.

Start from the user's last message before they asked. Anything still open goes in however old it is; Done covers only what finished since then.

## Gather

Keep it read-only: change nothing, start nothing, post nothing.

1. **Check the record:** commits since then, branches and worktrees with any uncommitted changes, open PRs with their checks and reviews, and the tracker if there is one. If that would fill your context, send an agent to read it and bring back only the rows.
2. **Add what's live:** agents and sidebars still out or that reported back, and every open ask, even one raised before the user's last message. Check each against the record rather than your memory: an agent you think is running may have landed, and a PR may have merged.

With no session to draw on, such as when an agent is sent for a project's catch-up, the record alone is the catch-up, starting from a time the asker gives or a day back.

## The table

Start with one line saying how many things need the user, or that nothing does. Then one table, with a row per piece of work, such as a PR, a ticket or an agent, never one per commit:

| Status | Item | Next step |
|---|---|---|

- **Status** is one of Needs you, Problem, In progress, Waiting on others or Done. Sort the rows in that order.
- **Item** names the work the way the user knows it, and where it is, such as a PR number or a branch.
- **Next step** says who does what next. For Needs you, it's what the user has to decide or do; for Done, what follows, or "None".

Write each row in plain words that stay true when read alone. Keep the columns as they are, since tables from several projects may be combined. Nothing goes after the table.
