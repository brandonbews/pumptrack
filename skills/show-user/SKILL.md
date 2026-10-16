---
name: show-user
description: Show the user something to look at, such as a file, a diff or a report, the way they like to see that kind of thing, instead of handing them a path. Use whenever you want the user to read or look at something, such as a plan, a skill, code, a branch's changes or a report.
---

# Show the user

**Your goal:** put the thing in front of the user the way they like to see it, so they don't have to find it and open it themselves.

## What it covers

- **A file,** such as a plan, a skill or code.
- **A diff:** a branch's own changes, a PR, a commit or uncommitted work.
- **A report,** such as `catch-up`'s table.

## Their way

How they like to see each kind of thing lives in the user's own agent instructions, the ones every session on their machine loads. Look there for this kind of thing and do what it says, such as a viewer in a new terminal tab, their editor, or a page in the browser. Where the project's instructions rule something out, such as hosted pages, they win.

Then tell the user where it is, such as the tab's number and label, or the link.

## Nothing set yet

If you can talk to the user, ask how they'd like to see this kind of thing, offering what you find on their machine: a terminal multiplexer, viewers for files and diffs, an editor, a page, or the conversation itself. Show it their way, then offer to save the answer to their own instructions so no session asks again. Write it only with their OK.

If you can't ask, as when another session sent you, fall back:

- **A file:** its full path.
- **A diff:** a one-line `git diff` command. For a branch, compare it with the branch it was cut from, the nearest other branch below it in its history, so a stacked branch shows only its own commits.
- **A report:** in the conversation.
