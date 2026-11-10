---
name: review-pr
description: Review a GitHub pull request, post the findings the user keeps as a pending review in their name, and submit it on their word. On a PR the user has reviewed before, check whether their comments were resolved and say whether it's ready to approve. Use when asked to review or re-review a PR.
---

# Review a PR

**Your goal:** handle the GitHub side of reviewing a pull request, and leave the judging to `review`.

## What you need

- **Whether to start over:** on a PR the user has reviewed before, re-review it unless they ask for a fresh full review.
- **The user's picks,** if you were sent back with them: skip to Post, and post them as given on the commit named.

## Gather

1. **What's been said:** reviews, inline threads with their replies and whether each is resolved (GitHub's GraphQL API has the thread state), and conversation comments.
2. **The user's earlier reviews:** submitted reviews by the user's login. If the user already has a pending review on the PR, post nothing new, since GitHub allows one per person. Submit it if that's what the user asked for, and otherwise say so under "Needs you" and stop.

Check out the PR's head in a checkout of its own, so the user's own checkout is untouched: one from your tool if it gives them out, or a worktree inside the project, since tools often let you write only there, in a folder git ignores. Remove it when you're done.

## Review

Run `review` in a fresh agent, with leave to start the agents its skill calls for, and hand it:

- **First review:** the goal, the PR's change as GitHub shows it (only the PR's own changes, with nothing the base gained since), and what's been said, so it doesn't repeat it.
- **Re-review:** the goal, the user's earlier comments with their replies, what others have said since, so it doesn't repeat it, and the change since the commit the user last reviewed. Count only the PR's own changes: if the base was merged in since, compare the PR's diff at that commit with its diff now. If that commit isn't in the head's history, as after a rebase, review the whole PR and say so. Say it's ready to approve when `review` says ready.

## Post

1. Go through the findings with the user, and keep the ones they pick, worded as they want.
2. Post them as a pending review on the commit you reviewed: one comment per finding on its line, and no approve, request-changes or comment action yet, since any of those submits it for everyone to see. Check it's still pending before you report, and say so first if it isn't. GitHub only takes comments on lines in the diff, so findings elsewhere go in the summary.
3. Write the summary and show it to the user. Keep it in a temp file, named in your report, rather than on GitHub until submitting: GitHub's own dialog opens with an empty box and replaces a summary set through the API with it.
4. Submit only when the user says to, with the event they choose (approve, request changes or comment; on the user's own PR, only comment) and the summary, submitting the pending review if there is one, or a new review if not.

If you can't ask the user, stop before posting and report. You'll be sent back with the user's picks.

## Report

Report the way `communication` says, with an outcome such as "4 findings on #42 for you to pick" or "#42 is ready to approve", and asks such as which findings to post and whether to submit. Then the commit you reviewed, `review`'s findings, and on a re-review each earlier comment and where it stands.
