---
name: sidebar
description: Spin a deep topic off into a fresh session the user works in directly, while this one keeps going, and hear back when it's done. Use when a topic needs a lot of back and forth with the user, such as grilling a plan or an open-ended exploration, or when the user asks for a prompt for another session.
---

# Sidebar

**Your goal:** give a deep topic a session of its own, so the user can work through it there while yours stays light and keeps going.

## Write the brief

The new session starts knowing nothing, so the brief stands alone. Write it to a file in a temp folder, covering:

- **Where it is:** the project's path, that the user works there directly, and this session's name, which is waiting to hear back.
- **The goal,** and the skill that fits it, such as `grill`.
- **What to read first,** and the sources to draw on.
- **What's settled,** so it isn't reopened, and **what's open** for the user to decide.
- **How to run it:** the steps, where to leave the outcome, and how to land what it changes.
- **Reporting back:** its last step is a short message to this session by name, with the outcome in one line, a "Needs you" list or "Nothing", and a line or two on where things are. If it can't send one, it tells the user so they can pass it on.

## Open it

If the user's own agent instructions say how to open a new session with the brief already sent, such as from a terminal multiplexer's command line, do it that way. Start the session under a name that marks it as a sidebar, such as `<project>-sidebar-<topic>`, and tell the user where it is.

Otherwise, give the user a one-line command to start a fresh session with: "Read <path> and follow it". Never a block to copy: long text selected from a terminal can arrive with characters missing, and the next agent fills the gaps silently, while a damaged path fails loudly.

Either way, keep it in your "Needs you" list until the user says they've started it, or it reports back.

## While it runs

Keep going on your own work. When it reports back, pass its "Needs you" on to the user, and read its outcome only when you need it.
