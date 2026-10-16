# Workflow

How to check, track and land work in this repo. The rules in `CLAUDE.md` come first.

## Checks

- `python3 evals/check_delegation.py` checks the eval's own logic at no model cost. Run it after any change under `evals/`.
- `python3 evals/delegation.py` runs the real eval through Claude Code's headless mode. It needs the `claude` command logged in and costs about $3 a run, so run it only after changing a skill it checks.
- A change to a README diagram gets rendered with mermaid-cli (`mmdc`) to a PNG, and the picture gets looked at before the change lands.

There are no other tests, no linter and no CI.

## Work

There's no tracker. The open questions are listed at the end of `internal/DESIGN.md`.

## Docs

Design decisions go in `internal/DESIGN.md` and credits in `internal/CREDITS.md`, as `CLAUDE.md` says. Both live in the private clone, which may be missing.

## Landing

- Work goes on a branch, and lands as a PR to `main`.
- Commit and push only when Brandon says so for that piece of work. He merges.
- A merge sets nothing off.
- Commits name no agent.

## The app

There's no app to run. The evals do the checking that a verify skill would do elsewhere.
