---
name: build
description: Build a change and land it, from gathering what's asked through a fresh review to a commit, a PR or a merge, the way the project lands work. Use for any feature, fix or other change to the project, including fixes from a review or PR feedback.
---

# Build

**Your goal:** land a change that does what was asked and is proven to work, so whoever sent you only has to read your report.

## What you need

- **The work:** a ticket, plan, PR comment, review finding or the brief itself. Given a ticket reference, fetch it from the tracker.
- **Where it lands:** from the brief, else the project's instructions. If neither says, ask.
- **The project's conventions:** its agent instructions, contributing guide, and how it runs its tests, lint and formatting.

## Steps

1. **Gather the requirements.** Read the work wherever it's described, then the code it touches, and say what done looks like. Put the user's calls, such as scope or how something should behave, to them before you build, as `communication` says.
2. **Build it** following `principles`, in small steps that each end in a check. For a bug, write a failing test first when one is cheap. Work on any branch the checkout isn't already on is built in a worktree of your own, inside the project in a folder git ignores, such as the one your tool uses for worktrees, so the user's checkout and other agents are untouched; remove the worktree once your work is committed, leaving the branch.
3. **Prove it works** with what the project has: its tests, lint and formatting, and driving the app if the project has a way to. Note what ran and what it showed.
4. **Get a fresh review** of anything beyond a typo or a one-line fix: hand the goal and the change to `review` in a fresh agent. If you can't start one, run it yourself and say so. Fix what must be fixed, and what should be fixed within the goal, then prove it again.
5. **Land it** (below).

## Land it

Land it the way the brief says, else the project's instructions, and ask if neither says. It's usually one of:

- A commit on the branch you were given.
- A branch and a PR into the branch you were given, or the default one, ready for review with CI passing. Wait for CI and fix what fails.
- The same, then merged once CI passes and it's proven to work end to end. Merge only where the brief or the project says to.

Fixing feedback on a PR, commit on its branch without pushing: pushing waits for the user's word. Where the project says to ask before pushing, ask, or if you can't, stop and report it.

Commits follow the repo's style and name no agent: no co-author trailer or other line crediting it, even if your tool adds one by default.

## Report

Report the way `communication` says, with an outcome such as "PR #12 open, CI green" or "Landed abc123 on main". Then what changed, what ran and what it showed, what the review found and what you did about each finding, the calls you made, and a link to the commit or PR.
