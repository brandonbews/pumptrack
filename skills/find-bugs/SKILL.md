---
name: find-bugs
description: Find the real bugs in a code change, prove each as far as is cheap, and say how sure you are of each. Use when asked to look for bugs, when reviewing a change, or when `review` hands you one.
---

# Find bugs

**Your goal:** find the bugs that are really there, and show how sure you are of each, so nobody chases a false alarm.

Look only for bugs: code that does something other than what's intended, security holes included. Style and design belong to `review`.

## What you need

The change (a diff, branch, PR or commits), the goal if there is one, since it says what's intended, and any limits, such as files to leave alone.

## Steps

1. **Read the change,** and work out what it now does differently, including what the diff doesn't spell out.
2. **Check its promises.** Compare what the code promises in its names, docs and comments, and what the goal says, with what it actually does.
3. **Look where a search stops.** Callers are quick to find, so go further: data other code reads (a stored field, an API response, a file format), when things run (startup, teardown, retries, two at once), and the source of the libraries it calls, at the version the project uses.
4. **Prove each suspect** as far down this scale as is cheap, and note where it stopped:
   1. Said so. Worth nothing on its own.
   2. Pointed at the line: a real `path:line`, or the library's own source.
   3. Traced: walked the bad case step by step, and it reaches the failure.
   4. Ran it: a script or test that calls the real code fails.
   5. Reproduced it in the running app, started the way the project's notes say.

   Scripts go in a temp folder, not the project. A suspect that tracing shows can't happen is cleared.
5. **Find the cause.** For each bug, name the root cause and check whether the same pattern appears elsewhere.

## Report

Report the way `communication` says, with an outcome such as "2 bugs, 1 proven by a failing test". Then:

- **Bugs:** traced or better. For each: `path:line`, how it breaks (what input or state leads to what wrong result), how bad it is, how sure you are, with the proof pasted for anything you ran, and the fix.
- **Unconfirmed:** suspects only pointed at, each with the cheapest way to settle it.
- **Cleared:** what you checked and ruled out, a line each.
