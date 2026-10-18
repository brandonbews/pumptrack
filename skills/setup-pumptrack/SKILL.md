---
name: setup-pumptrack
description: Install pumptrack's skills and set a project up for them, recording how its checks run, where work is tracked, where docs go and how work lands, and setting up the user's own preferences. Use when installing pumptrack, or when asked to set a project up for it or change that setup.
---

# Set up pumptrack

**Your goal:** set the project up so pumptrack's skills work here without stopping to ask. Find what you can yourself, and ask the user only the rest.

It's safe to run again: check what's already set, and ask only about what's missing or what the user wants to change. Sent back with the user's answers and the draft notes, skip to Do it.

## Look first

Change nothing yet.

- **Install:** whether pumptrack's skills are installed for this project, in its skills folder or the user's personal one. Note any skill already installed with the same name or doing the same job, such as another code review skill, since the two compete for the same requests, and which one the tool lets win.
- **The project:** read its agent instructions, README, contributing guide, build and package files, CI config, connected tools, git remote and remote branches. Look for:
  - **Checks:** the commands for tests, lint, formatting and type checks. Run each one this machine can, in its check-only form where it has one, skipping any that touches something shared, such as a deployment, and revert anything a check changes, counting it as failed. Note any that fail, and what the machine lacks for the rest, such as secrets, a service or another machine, without working around it.
  - **Work:** where it's tracked, such as an issue tracker, Jira or a file.
  - **Docs:** where plans, design notes and reports go, if anywhere.
  - **Landing:** commits to the main branch, PRs or stacks; whether to ask before pushing; and who merges, and what a merge sets off, such as a deploy.
  - **Glossary:** whether the project keeps one, and where.
  - **The app:** whether users run something, such as a site, a CLI or an API, and whether agents have a way to start it, drive it the way a user does and keep proof.
- **The user and the machine:** these differ by person and machine, not by project, so they belong in the user's own setup. Check their own settings, not your environment, which whoever started you may have set.
  - **Talking to them:** pumptrack's skills talk to the user the way `communication` says, but a skill loads only when something points to it. Offer to add one line to their own agent instructions, such as "Talk to me the way the `communication` skill says", so every session does.
  - **Seeing things:** how they like to see Markdown, code, diffs and reports, as `show-user` asks.
  - **Opening sessions:** how they'd like `sidebar` to open a new session with its brief already sent: the tool and the exact commands that open a tab, start the agent and send the brief, or just a one-line command to run. Don't pick a tool for them, even when only one is installed. The answer goes in their own agent instructions, where `sidebar` looks.
  - **How deep agents go:** the deepest chain is four agents below the session: `address-pr-feedback`, `build`, `review` and `find-bugs`, under `pumptrack`. Some tools cap it lower, as Claude Code's `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` does at three by default. Below four the skills still work, but the last step loses its fresh context.
  - **The lookout:** `pumptrack-lookout`, in pumptrack's repo, catches the user up across all their projects and lets them direct work in any of them. It goes in the skills folder of the folder that holds their projects, not in any one project.

## Ask, in one round

Ask everything in one round, the way `communication` says, and skip what's already settled.

- **Install,** if needed: in the project, committed for everyone or kept out of git for this clone only (through the file `git rev-parse --git-path info/exclude` names), or just for the user, in their personal skills folder for every project on this machine. And what to do about each clash.
- **What you couldn't find** about the project.
- **Where to keep the notes:** the place the project already uses for docs like these, or `docs/agents/workflow.md` if it has none, and whether to commit them or keep them out of git.
- **The user's setup:** anything above that isn't set yet.
- **What's missing:** offer to have each missing or failing check set up or fixed with `build`, and `create-verify-skill` for an app agents can't drive.

If you can't ask the user, stop here and report your questions and the draft notes. You'll be sent back with their answers.

## Do it

Show the user a draft of the notes first.

1. **Install** the skills: copy each folder under `skills/` in pumptrack's repo, https://github.com/brandonbews/pumptrack, into the folder the user chose. Or link them, to pick up every change, from a clone that stays where it is; they follow whichever branch it has checked out. The folder differs by tool, so ask if you're not sure which it is.
2. **Write the notes:** what you found and what the user answered, under plain headings such as Checks, Work, Docs, Landing, Glossary and The app. Point to what the project's instructions and docs already say rather than repeating it, and keep pumptrack's name out: the notes describe the project.
3. **Add a pointer** in the project's agent instructions: one line saying what the notes cover and where they are, such as "How to check, track and land work here: `docs/agents/workflow.md`". If the notes stay out of git, the pointer goes somewhere out of git too, such as a local instructions file your tool loads. Ask before creating an instructions file.
4. **Land** what's committed the way the project lands work, with commits that name no agent, as `build` says. Change the user's setup as they agreed, and follow up the offers they took.

## Report

Report the way `communication` says, with an outcome such as "Set up: notes in `docs/agents/workflow.md`, lint failing", and among the asks what this machine lacks to run every check. Then what you recorded and where, what you changed in the user's setup, and what you left unset.
