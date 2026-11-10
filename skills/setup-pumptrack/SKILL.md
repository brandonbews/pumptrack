---
name: setup-pumptrack
description: Install pumptrack's skills and set a project up for them, recording how its checks run, where work is tracked and how work lands, and setting up the user's own preferences. Use when installing pumptrack, or when asked to set a project up for it or change that setup.
---

# Set up pumptrack

**Your goal:** set the project up so pumptrack's skills work here without stopping to ask. Find what you can yourself, and ask the user only the rest.

It's safe to run again: check what's already set, and ask only about what's missing or what the user wants to change. Sent back with the user's answers and the draft notes, skip to Do it.

## Look first

Change nothing yet.

- **Install:** whether pumptrack's skills are installed for this project, in its skills folder or the user's personal one. If they're linked, any skill in the clone that isn't linked yet, or link whose skill is gone, counts as missing. Note any skill already installed with the same name or doing the same job, such as another code review skill, since the two compete for the same requests, and which one the tool lets win.
- **The project:** read its agent instructions, README, contributing guide, build and package files, CI config, connected tools, git remote and remote branches. Look for:
  - **Checks:** the commands for tests, lint, formatting and type checks. Run each one this machine can, in its check-only form where it has one, skipping any that touches something shared, such as a deployment, and revert anything a check changes, counting it as failed. Note any that fail, and what the machine lacks for the rest, such as secrets, a service or another machine, without working around it.
  - **Work:** where it's tracked, such as an issue tracker, a board or a file.
  - **Landing:** commits to the main branch, PRs or stacks; whether to ask before pushing; and who merges, and what a merge sets off, such as a deploy.
  - **The app:** whether users run something, such as a site, a CLI or an API, and whether agents have a way to start it, drive it the way a user does and keep proof.

## The user's setup

This differs by person and machine, not by project, so it belongs in the user's own setup.

- **Talking to them:** pumptrack's skills talk to the user the way `communication` says, but a skill loads only when something tells the agent to load it, and naming it isn't enough. Offer to add one line to their own agent instructions that does, such as "Load the `communication` skill when you start, and talk to me the way it says", so every session does. Offer it only when the skills are, or will be, installed in their personal skills folder, since those instructions load in every project.

## Ask, in one round

Ask everything in one round, the way `communication` says.

- **Install,** if needed: in the project, committed for everyone or kept out of git for this clone only (through the file `git rev-parse --git-path info/exclude` names), or just for the user, in their personal skills folder for every project on this machine. And what to do about each clash.
- **What you couldn't find** about the project.
- **Where to keep the notes:** the place the project already uses for docs like these, or `docs/agents/workflow.md` if it has none, and whether to commit them or keep them out of git.
- **The user's setup:** anything above that isn't set yet.
- **What's missing:** offer to have each missing or failing check set up or fixed with `build`, and `create-verify-skill` for an app agents can't drive.

If you can't ask the user, stop here and report your questions and the draft notes. You'll be sent back with their answers.

## Do it

Show the user a draft of the notes first.

1. **Install** the skills: copy each folder under `skills/` in pumptrack's repo, https://github.com/brandonbews/pumptrack, into the folder the user chose. Or link them, to pick up every change, from a clone that stays where it is; they follow whichever branch it has checked out. Links go one per skill, so on a rerun, link any skill that's new and remove links whose skill is gone. The folder differs by tool, so ask if you're not sure which it is.
2. **Write the notes:** what you found and what the user answered, under plain headings such as Checks, Work, Landing and The app. Point to what the project's instructions and docs already say rather than repeating it, and keep pumptrack's name out: the notes describe the project.
3. **Add a pointer** in the project's agent instructions: one line saying what the notes cover and where they are, such as "How to check, track and land work here: `docs/agents/workflow.md`". If the notes stay out of git, the pointer goes somewhere out of git too, such as a local instructions file your tool loads. Ask before creating an instructions file.
4. **Land** what's committed the way the project lands work. Change the user's setup as they agreed, and follow up the offers they took.

## Report

Report the way `communication` says, with an outcome such as "Set up: notes in `docs/agents/workflow.md`, lint failing", and among the asks what this machine lacks to run every check. Then what you recorded and where, what you changed in the user's setup, and what you left unset.
