---
name: pumptrack-lookout
description: Catch the user up across all their projects at once, by asking every running session for a catch-up and combining the answers into one report. Use from the folder that holds the user's projects, when they ask to catch up on everything or where things stand across projects, and as their place to direct work across them.
---

# Lookout

**Your goal:** give the user one place to see where things stand and direct work across all their projects, while each project's own session does it.

## Ask each session

Message every other session running on this machine, asking it for a catch-up with `catch-up`. Give your session's name to reply to, and ask for its project folder and the table, nothing else. If the user gave a time to start from, pass it on.

Ask them all, without sorting them first, since `catch-up` scopes itself to its session.

The user may have walked away, so don't stop the catch-up to ask them anything. A session waiting on the user's input, such as a question or an approval, can't answer until they give it, so don't wait for it: give it a Needs you row at the top of the report saying so, with what it's waiting on if you can tell. Give the rest a few minutes, then report with what's come in, a row for each session that hasn't answered, and pass later answers on as they arrive.

## Combine

Put the tables together into one, adding a Project column:

| Status | Project | Item | Next step |
|---|---|---|---|

Where two rows name the same piece of work, such as a sidebar's own row and its `pumptrack` session's row for it, keep one, with the more current status and next step. Sort the rows by status in `catch-up`'s order, then by project. Start with one line saying how many things need the user, or that nothing does.

## Report

Where you can publish a page, publish the report as one titled "Lookout", and give the user the link. Update the page you published last time, found by its title, so the link stays the same and the user can pin it. Otherwise, show the table.

## Direct the work

The user may direct work in any project from here. Stay light, as `pumptrack` does: message the session that owns the project with what the user asked and your session's name to reply to, then pass its reply on. Never do a project's work yourself. Where a project has no session, offer to open a `pumptrack` session there, the way `sidebar` opens one, named for the project and with the request as its brief.
