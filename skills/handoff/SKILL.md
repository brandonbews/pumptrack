---
name: handoff
description: Gather a session's live state into a handoff file, so the work carries on after a compact or a clear, or in a fresh session, with nothing to paste. Use when the user asks for a handoff, or says they're about to compact, clear or start fresh, and when a session starts and a handoff is waiting for it.
---

# Handoff

**Your goal:** get everything live out of the conversation and into one file, so whoever comes next, this session after a compact or a fresh one, picks up where you left off.

## Where it goes

`.pumptrack/handoff.md` in the project, kept out of git for this clone only: add it to the file `git rev-parse --git-path info/exclude` names, if it isn't there. If the project's instructions name another place, such as one that syncs to another machine, use that.

## Write one

1. **Record first.** Put decisions not yet recorded, and work not yet in the tracker, where the project keeps them, so the handoff points to files rather than carrying them.
2. **Agents still running** keep going through a compact, but may not survive a clear or a new session. Before either, wait for them to land, unless the user says not to.
3. **Write the handoff,** replacing any already there:
   - What this session is, such as a `pumptrack` session, and the skill to start it with.
   - What to read first: the files that hold the state.
   - Where things stand: what's done, and what's next.
   - Every open ask: the questions and actions waiting on the user.
   - Each agent and sidebar still out: its task, and where its work is, such as a branch or a PR.
   - How the user works, where the project's instructions don't say.
   - Last: "Delete this file once you've picked it up."
4. **Tell the user** it's ready, and how to pick it up: after a compact or a clear, start the session's skill again, such as `/pumptrack`. In any other session: "Read <path> and follow it".

## Pick one up

When a session starts, look for a handoff for this project. If there's one, read it, and what it names only as far as you need, sending an agent for anything bulky. Delete it, and tell the user what you picked up. Start with the outcome in one line, then a "Needs you" list of the open asks, or "Nothing".
