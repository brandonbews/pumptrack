---
name: sidebar
description: Spin a deep topic off into a fresh session the user works in directly, while this one keeps going, and hear back when it's done. Use when a topic needs a lot of back and forth with the user, such as grilling a plan or an open-ended exploration, or when the user asks for a prompt for another session.
---

# Sidebar

**Your goal:** give a deep topic a session of its own, so the user can work through it there while yours stays light and keeps going.

## Write the brief

Write the brief to a file outside the project, such as in a temp folder, where the new session can read it, covering:

- **Where it is:** the project's path, that the user works there directly, and how to reach this session, which is waiting to hear back, such as its name or its link in your tool.
- **The goal,** and the skill that fits it, such as `grill`.
- **What to read first,** and the sources to draw on.
- **What's settled,** so it isn't reopened, and **what's open** for the user to decide.
- **How to run it:** the steps, where to leave the outcome, and how to land what it changes.
- **Reporting back:** its last step is a short message to this session, reporting the way `communication` says, with a line or two on where things are, and telling the user plainly that the sidebar is done. If it can't send one, it tells the user so they can pass it on.

## Open it

Open it once the user agrees to it, with the brief already sent, the first way that fits:

1. The user's own agent instructions, if they say how, such as from a terminal multiplexer's command line.
2. The tool you run in, if it can open a new session the user works in directly, with its first message, such as an app that keeps sessions side by side.
3. A one-line command for the user to start a fresh session with: "Read <path> and follow it". Never a block to copy: long text selected from a terminal can arrive with characters missing, and the next agent fills the gaps silently, while a damaged path fails loudly.

Give it a short name that marks it as a sidebar, such as `<project>-sidebar-<topic>`, and tell the user where it is, such as a tab or a link.

Whichever way, keep it in your "Needs you" list until the user says they've started it, or it reports back.

## While it runs

When it reports back, pass its "Needs you" on to the user, and read its outcome only when you need it.
