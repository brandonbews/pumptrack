# pumptrack

Open-source agent skills for orchestrating coding agents. An agent installs them by cloning this repo and copying `skills/` into a project. A personal project of Brandon's, to be published on GitHub for anyone to use. The repo stays private until then, but everything in it is written as public. Design notes live in `internal/DESIGN.md`.

## Layout

- `skills/<name>/SKILL.md`: one folder per skill. Only `skills/` gets copied into projects, so repo files (README, this file) stay outside it.
- `pumptrack-lookout/SKILL.md`: the lookout, kept beside `skills/` because it goes in the folder above the user's projects, not into each one.
- `evals/`: scripted checks of how the skills behave, run through Claude Code's headless mode. Each run uses real model time, about $3 at API prices, so run one after changing the skill it checks. `python3 evals/check_delegation.py` checks the eval's own pass and fail logic against hand-made states, at no model cost.
- `docs/agents/workflow.md`: how to check, track and land work here.
- `internal/`: a gitignored clone of the private `brandonbews/pumptrack-internal` repo, which holds the design notes. It may be missing, and that's fine. To set it up on a computer, follow the README's "Private notes".

## Rules

- **Keep it light.** Build the smallest thing that works. No files, settings or structure ahead of need, and no designing pieces we aren't about to build. Skills grow in small steps with light prose, so each new instruction is easy to see.
- **Everything in this repo is public.** Nothing from private projects goes in: no internal names, paths, hostnames, client details or secrets. When a skill comes over from a private repo, strip whatever is specific to that project before committing it.
- **Skills stay portable.** Frontmatter keeps to the [Agent Skills spec](https://agentskills.io/specification), with `name` matching the folder name; a Claude Code-only field needs a reason recorded in the design notes. Bodies say what to do in plain terms instead of naming Claude Code's tools. Claude-specific wiring, such as hooks, stays out of the skill folders.
- **Credit what we draw on** in `internal/CREDITS.md`: one line per person or project, saying what we took or learned from it.
- **A README diagram change gets rendered and looked at before it lands**, with a Mermaid renderer, so what's checked is the picture rather than the source.
- **Commits name no agent.** No `Co-Authored-By` trailer or other line crediting the agent, the same as pumptrack's skills do in other projects.
- **Record design decisions in `internal/DESIGN.md`**, committed in that repo, as they're made: the decision, the date and the reason, in plain prose. Don't quote Brandon. Revise a decision in place with a note rather than adding a contradicting one.
