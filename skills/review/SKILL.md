---
name: review
description: Review a code change against its goal and the project's principles, and report only the findings that matter. Use for a builder's change before it lands, someone's PR, or a re-review, or whenever asked to review code, a branch or a PR.
---

# Review

**Your goal:** say whether a change does what it set out to do, cleanly, and report only the findings worth acting on.

## What you need

- **The goal:** a ticket, plan, PRD or PR description. If you weren't given one, look in the PR, the commits or the tracker. If there's none, say so under "Needs you" and review against the principles alone.
- **The change:** a diff, branch, PR or commits. If you weren't told, review the current branch against the branch it was cut from, and say so. If it's unclear what to review, ask.
- **Earlier comments,** on a re-review.
- **The project's conventions:** its agent instructions, contributing guide, and lint and format configs.

## Review it

1. Hand the change, the goal and any limits you were given to `bug-check` in a fresh agent, so it runs alongside you. If you can't start one, run it yourself after your own pass. Leave hunting and proving bugs to it. If you spot a likely bug it didn't report, add it to its unconfirmed leads.
2. **The goal.** Check that everything it asks for is done, and nothing beyond it was added.
3. **The principles.** Check the change against `principles`. Read the tests that cover the changed code, not only the changed tests, and flag changed behavior that no test would catch breaking.
4. **Earlier comments.** Say whether each was resolved, not resolved, or answered, and whether the answer holds.
5. **Keep what matters.** Keep a finding only if it's a bug, a gap against the goal, or a broken principle that will cost a reader or caller. Drop matters of taste. Where the right call turns on intended behavior or a preference you can't find in the code or docs, ask under "Needs you" rather than guess.

Change nothing and post nothing while reviewing.

## Report

Start with the verdict in one line: ready, or not and why. Then a "Needs you" list of every question and action for the user, or "Nothing". Then the findings, grouped:

- **Must fix:** blocks landing. The goal not met, security holes, tests that hide a defect, and bugs bad enough to block.
- **Should fix:** worth fixing now, because it will cost later.
- **Optional:** judgment calls, fine to skip.

For each: `path:line`, the problem, why it matters (the goal or principle it misses), and the fix, specific enough to act on without redoing the review. Place each of `bug-check`'s bugs by how bad it is, keeping its word on how sure it is, and where a bug and a principle finding share a cause, make them one finding. Its "Needs you" items join yours, its unconfirmed leads follow the findings as their own short list, and its cleared list stays out. On a re-review, list each earlier comment and where it stands.

## Fixing afterward

If asked afterward to fix findings, fix each approved one in its own commit, with no co-author trailer for the agent, and don't push unless asked. Recap with a line per commit, plus anything skipped.
