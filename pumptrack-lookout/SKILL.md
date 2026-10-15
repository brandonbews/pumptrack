---
name: pumptrack-lookout
description: Catch the user up across all their projects at once, by asking every running session for a catch-up and combining the answers into one report. Use from the folder that holds the user's projects, when they ask to catch up on everything or where things stand across projects.
---

# Lookout

**Your goal:** give the user one view of where things stand across all their projects, built from what each running session reports.

## Ask each session

Message every other session running on this machine, asking it for a catch-up with `catch-up`. Give your session's name to reply to, and ask for its project folder and the table, nothing else. If the user gave a time to start from, pass it on.

Ask them all, without sorting them first: a pumptrack session covers its project, and any other session covers its thread, such as a sidebar's topic.

The user may have walked away, so don't stop to ask them anything. A session waiting on the user's input, such as a question or an approval, can't answer until they give it, so don't wait for it. Give it a Needs you row at the top of the report saying so, with what it's waiting on if you can tell, and report once the rest have answered. If you can't message other sessions, say so, and suggest running `catch-up` in each.

## Combine

Put the tables together into one, adding a Project column:

| Status | Project | Item | Next step |
|---|---|---|---|

Where two rows name the same piece of work, such as a sidebar's own row and its orchestrator's row for it, keep one, with the more current status and next step. Sort the rows by status in `catch-up`'s order, then by project. Start with one line saying how many things need the user, or that nothing does.

## Report

Where you can publish a page, publish the report as one titled "Lookout", and give the user the link. Update the page you published last time, found by its title, so the link stays the same and the user can pin it. Otherwise, show the table.
