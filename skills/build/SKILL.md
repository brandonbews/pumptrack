---
name: build
description: Build a change and land it, from gathering what's asked through a fresh review to a commit, a PR or a merge, the way the project lands work. Use for any feature, fix or other change to the project, including fixes from a review or PR feedback.
---

# Build

**Your goal:** land a change that does what was asked and is proven to work, so whoever sent you only has to read your report.

## Steps

1. **Gather the requirements.** Read the work wherever it's described, such as a ticket, a plan, a PR comment, a review finding or the brief itself, fetching a ticket given by reference. Say what done looks like. Put the user's calls, such as scope or how something should behave, to them before you build, as `communication` says.
2. **Get a checkout of your own.** Never build in the user's checkout or switch its branch, even for a one-line fix, since they and other agents may be mid-work there. If your tool started you in a checkout made for this work, use it. Otherwise get one the way your tool gives out checkouts, or make a worktree inside the project in a folder git ignores, and remove it before you report, leaving the branch. Cut it from the branch the work lands on as committed, not from whatever is checked out.
3. **Build it** following `principles`. For a bug, write a failing test first when one is cheap.
4. **Prove it works** with what the project has: its tests, lint and formatting, and driving the app if the project has a way to.
5. **Get a fresh review** of the whole of the work you were given, once it's built and proven, not of each step or commit. Skip it for a typo or a one-line fix. Hand the goal and the change to `review` in a fresh agent, with leave to start the agents its skill calls for. If you can't start one, run it yourself and say so. Fix what must be fixed, and what should be fixed within the goal, in this build rather than new ones, then prove it again.
6. **Land it** (below).

## Land it

Land it the way the brief says, else the project's instructions, and ask if neither says. It's usually one of:

- A commit on the branch you were given. If the user has that branch checked out, commit on a branch of your own, fast-forward theirs to it and delete yours, the one thing you do in their checkout. If it won't fast-forward, stop and report.
- A branch and a PR into the branch you were given, or the default one, ready for review with CI passing. Wait for CI and fix what fails. If your tool says not to wait, report the PR, its head commit and where its checks stand instead, so whoever sent you can see it through.
- The same, then merged once CI passes and it's proven to work end to end. Merge only where the brief or the project says to.

When fixing a reviewer's feedback on a PR, commit on its branch and don't push: pushing waits for the user's word.

Commits follow the repo's style.

## Report

Report the way `communication` says, with an outcome such as "PR #12 open, CI green" or "Landed abc123 on main". Then what changed, what ran and what it showed, what the review found and what you did about each finding, and a link to the commit or PR.
