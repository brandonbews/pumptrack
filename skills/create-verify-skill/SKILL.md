---
name: create-verify-skill
description: Write a project a skill that starts its app, drives it the way a user does to prove a change works, keeps the proof and cleans up, with a map of the features users reach, then run it once. Use when a project has no scripted way to prove what a user sees, when `setup-pumptrack` offers it, or when asked for a verify skill.
---

# Create a verify skill

**Your goal:** give the project a skill that any agent, arriving cold in the middle of a task, can follow to start the app, use it the way a user does and prove a change works.

It covers what a user sees. Tests, lint and the rest stay the project's own checks.

## Study the repo

Answer these from the code, and ask the user only what you can't find:

- **Surface:** what a user touches, such as a web app, a CLI, a desktop app or an API. If there are several, pick the main one and note the rest.
- **Start:** the project's own command to run it locally, with its ports, environment, seed data and sign-in.
- **Drive:** a way to work it from a script. Use what the project already has, such as browser tests, before a generic way: a scripted browser for a web or desktop app, a terminal session for a CLI, plain HTTP for an API.
- **Proof:** what can be kept, such as screenshots, terminal output, responses, logs or stored data.
- **Side by side:** whether two copies can run at once, each with its own ports and data, and whether starting one changes anything shared, such as a database or deployment others use.

If it doesn't build or start as it is, fix that or report exactly what's wrong before writing anything. Adding a tool the project doesn't have, such as a browser driver, needs the user's OK.

## Write the skill

Name it `verify-<app>`, and put it where the project's skills are installed. Its description names the app and says to use it to prove a change in the running app, the way a user does. Fill every part with real commands from this repo, never placeholders:

- **Start:** the command that brings the app up from empty, with any migrations and seed data, how to tell it's ready to use rather than just running, and how to stop it.
- **Health check:** one read-only check that this copy is worth driving: it's up, it's running this checkout's code, and this run started it. Run it first, and again whenever something looks off. If two copies can't run side by side, say so, and never drive one this run didn't start.
- **Drive:** how to work it, with real selectors and commands. Prefer stable handles, such as labels, routes and prompts, over positions.
- **Proof:** what to keep and where, in a folder out of git. Go through the user's real path, not test-only shortcuts. Keep the action and its result, not just the final screen, and check side effects, such as stored data, as well as what's shown.
- **Clean up:** stop only what this run started, never by process name, and keep the proof.
- **The map:** read `features.md` before driving, and fix it whenever a drive finds it wrong.

Any script it ships is executable, and the skill shows how to run it.

## Map the features

Write `features.md` beside it, covering the three to five main features a user reaches, found from routes, commands, menus or docs. For each:

- What it is, as a user sees it.
- Every way a user gets to it.
- How to drive it: each step, with its exact command and what should happen.
- What proves it works.
- Gotchas that would waste or spoil a run.

If the seed data can't support a step, say why under its gotchas rather than weakening the step until it passes.

## Run it once

Follow the new skill end to end: start, health check, drive one feature from the map, keep the proof, clean up, then check the proof is still there. Fix what fails, cleaning up after each failed try, and run it again. Until it has run, it's a draft.

## Hand it over

If it's in the project, land it the way the project lands work. Add it to the project's notes for agents, the ones its instructions point to, so whoever builds a change knows to use it.

## Report

Start with the outcome in one line, such as "`verify-shop` written and run: drove checkout, proof kept". Then a "Needs you" list of every question and action for the user, or "Nothing". Then what the skill covers, what it leaves out, such as other surfaces or features not yet mapped, and anything the run couldn't reach.
