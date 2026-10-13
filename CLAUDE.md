# pumptrack

Open-source agent skills for orchestrating coding agents. An agent installs them by cloning this repo and copying `skills/` into a project. A personal project of Brandon's, published on GitHub for anyone to use. Design notes live in `internal/DESIGN.md`.

## Layout

- `skills/<name>/SKILL.md`: one folder per skill. Only `skills/` gets copied into projects, so repo files (README, this file) stay outside it.
- `internal/`: a gitignored clone of the private `brandonbews/pumptrack-internal` repo, which holds the design notes. It may be missing, and that's fine. To set it up on a computer, follow the README's "Private notes".

## Rules

- **Keep it light.** Build the smallest thing that works. No files, settings or structure ahead of need, and no designing pieces we aren't about to build. Skills grow in small steps with light prose, so each new instruction is easy to see.
- **Everything in this repo is public.** Nothing from private projects goes in: no internal names, paths, hostnames, client details or secrets. When a skill comes over from a private repo, strip whatever is specific to that project before committing it.
- **Skills stay portable.** Frontmatter keeps to the [Agent Skills spec](https://agentskills.io/specification), with `name` matching the folder name; a Claude Code-only field needs a reason recorded in the design notes. Bodies say what to do in plain terms instead of naming Claude Code's tools. Claude-specific wiring, such as hooks, stays out of the skill folders.
- **Record design decisions in `internal/DESIGN.md`**, committed in that repo, as they're made: the decision, the date and the reason, in plain prose. Don't quote Brandon. Revise a decision in place with a note rather than adding a contradicting one.
