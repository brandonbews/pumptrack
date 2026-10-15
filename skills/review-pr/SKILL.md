---
name: review-pr
description: Review a GitHub pull request, post the findings the user keeps as a pending review in their name, and submit it on their word. On a PR the user has reviewed before, check whether their comments were resolved and say whether it's ready to approve. Use when asked to review or re-review a PR.
---

# Review a PR

**Your goal:** handle the GitHub side of reviewing a pull request, and leave the judging to `review`.

## What you need

- **The PR:** a number or URL. If you weren't told, use the current branch's PR, and say so.
- **Whether to start over:** on a PR the user has reviewed before, re-review it unless they ask for a fresh full review.

## Gather

Use `gh` and GitHub's API.

1. **The PR:** its description, the ticket it links if any, its base and its head commit.
2. **What's been said:** reviews, inline threads with their replies and whether each is resolved (GitHub's GraphQL API has the thread state), and conversation comments.
3. **The user's earlier reviews:** submitted reviews by the user's login. If the user already has a pending review on the PR, say so under "Needs you" and post nothing, since GitHub allows one per person.

Check out the PR's head in a temporary worktree, so the user's own checkout is untouched, and remove it when you're done.

## Review

- **First review:** hand `review` the goal, the PR's change as GitHub shows it (`gh pr diff`, or a three-dot diff against the base), and what's been said, so it doesn't repeat it.
- **Re-review:** hand `review` the goal, the user's earlier comments with their replies, what others have said since, so it doesn't repeat it, and the change since the commit the user last reviewed, counting only the PR's own changes: if the base was merged in since, compare the PR's diff at that commit with its diff now. If that commit isn't in the head's history, as after a rebase, review the whole PR and say so. Approval is a yes when `review` says ready.

## Post

1. Go through the findings with the user, and keep the ones they pick, worded as they want.
2. Post them as a pending review on the commit you reviewed: one comment per finding on its line, and no `event`, which leaves the review pending and visible only to the user. GitHub only takes comments on lines in the diff, so findings elsewhere go in the summary. End every comment with `<sub>Written by an AI agent, reviewed by me.</sub>`.
3. Write the summary, ending with the same line, and show it to the user, but hold it back from GitHub until submitting. Submitting from GitHub's own dialog may drop a summary set through the API.
4. Submit only when the user says to, with the event they choose (approve, request changes or comment) and the summary: through the pending review's submit endpoint, or as a new review if nothing is pending.

If you can't talk to the user, as when another agent sent you, stop before posting and report. You'll be sent back with the user's picks.

## Report

Start with the outcome in one line, such as "4 findings on #42 for you to pick" or "#42 is ready to approve". Then a "Needs you" list of every question and action for the user, or "Nothing", such as which findings to post and whether to submit. Then `review`'s findings, and on a re-review each earlier comment and where it stands. Once anything is posted, link the PR.
