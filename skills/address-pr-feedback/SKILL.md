---
name: address-pr-feedback
description: Go through the open feedback on the user's own GitHub pull request, judge whether each item is valid, and once the user approves a plan, have each accepted fix built as its own commit and reply to the reviewers. Use when asked to address, handle or go through PR feedback or review comments.
---

# Address PR feedback

**Your goal:** answer every open piece of feedback on the user's PR, with a fix or a reasoned reply, and let the user decide which.

## What you need

The PR: a number or URL. If you weren't told, use the current branch's PR, and say so.

Sent back with the user's answers to a plan, skip to Act on it.

## Gather

Use `gh` and GitHub's API. Collect what's still open:

- Inline threads not yet resolved whose last comment isn't the user's, each with its replies as one item (GitHub's GraphQL API has the thread state). Flag any that a later push made outdated.
- Review summaries and conversation comments the user hasn't answered.

Note which authors are bots. Read the PR's goal too: its description, and the ticket it links if any.

## Judge

Hold each item to `review`'s bar: it's valid if it's a bug, a gap against the goal, or a broken principle that will cost a reader or caller. Hand items that claim a bug to `find-bugs` to prove or clear. A matter of taste is the user's call. Hold bots to the same bar as people.

## Plan

Show the user each item with its author and `path:line`, and one of:

- **Accept:** what the fix will be.
- **Push back:** why not, as you'd put it to the reviewer.
- **Ask:** the question for the user.

Change nothing until the user approves the plan. If you can't talk to the user, as when another agent sent you, stop here and report the plan. You'll be sent back with their answers.

## Act on it

1. Hand each accepted item to `build` in a fresh agent, with the reviewer's words. Send them one at a time, so they don't collide on the branch, and each lands as its own commit on the PR's branch.
2. Push only when the user says to.
3. Draft a reply for each item: what changed, with the commit, or why not. Post the replies only when the user says to, in the item's thread or, for a review summary or conversation comment, in a conversation comment that quotes or links it. Never resolve threads.
4. Offer to re-request review from the reviewers who left feedback, and do it on the user's word.

## Report

Start with the outcome in one line, such as "5 open items on #42: 3 to fix, 1 to push back, 1 for you". Then a "Needs you" list of every question and action for the user, or "Nothing", such as approving the plan, pushing, posting the replies and re-requesting review. Then the plan, or once acted on, a line per commit, the drafted replies, and anything skipped.
