# pumptrack

Open-source agent skills for orchestrating coding agents. An agent installs them by cloning this repo and copying `skills/` into a project. A personal project, to be published on GitHub for anyone to use. The repo stays private until then, but everything in it is written as public.

## Layout

- `skills/<name>/SKILL.md`: one folder per skill. Only `skills/` gets copied into projects, so repo files (README, this file) stay outside it.
- `pumptrack-lookout/SKILL.md`: the lookout, kept beside `skills/` because it goes in the folder above the user's projects, not into each one.
- `evals/`: scripted checks of how the skills behave, run through Claude Code's headless mode.
- `internal/`: a gitignored clone of the private `pumptrack-internal` repo, which holds the roadmap (`ROADMAP.md`). It may be missing, and that's fine; the skills work the same without it. To set it up on a computer, from this checkout:
  1. `git clone https://github.com/brandonbews/pumptrack-internal.git internal`
  2. `sh internal/scripts/install-hooks.sh`, which installs a `post-checkout` hook that links `internal` into every new worktree. It's safe to rerun, and it refuses to replace a hook it didn't write.

## Rules

- **Keep it light.** Build the smallest thing that works. No files, settings or structure ahead of need, and no designing pieces we aren't about to build. Skills grow in small steps with light prose, so each new instruction is easy to see.
- **Everything in this repo is public.** Nothing from private projects goes in: no internal names, paths, hostnames, client details or secrets. When a skill comes over from a private repo, strip whatever is specific to that project before committing it.
- **Don't name the person working on pumptrack in the repo.** Where a line needs someone, it's "the maintainer" or "the user". A GitHub URL or `owner/repo` slug that something needs in order to work, such as a clone URL, can stay.
- **Skills stay portable.** Frontmatter keeps to the [Agent Skills spec](https://agentskills.io/specification), with `name` matching the folder name; a Claude Code-only field needs a good reason. Bodies say what to do in plain terms instead of naming Claude Code's tools. Claude-specific wiring, such as hooks, stays out of the skill folders.
- **Credit what we draw on** in the README's "Credits" section: one line per person or project, saying what we took or learned from it.
- **The private repo's `ROADMAP.md` holds ideas, tickets and plans not yet built.** An entry comes out once it's built; the skills and the repo are their own record of what's built.

## Checks

- `python3 evals/check_delegation.py` checks the eval's own pass and fail logic against hand-made states, at no model cost. Run it after any change under `evals/`.
- `python3 evals/delegation.py` runs the real eval through Claude Code's headless mode. It needs the `claude` command logged in and costs about $3 a run at API prices, so run it only after changing a skill it checks.
- A change to a README diagram gets rendered with mermaid-cli (`mmdc`) to a PNG, and the picture gets looked at before the change lands.

There are no other tests, no linter, no CI and no app to run; the evals do the checking a verify skill would do elsewhere.

## Work and landing

- There's no tracker beyond `internal/ROADMAP.md`.
- Work goes on a branch, and lands as a PR to `main`.
- Commit and push only when the maintainer says so for that piece of work. The maintainer merges.
- A merge sets nothing off.
