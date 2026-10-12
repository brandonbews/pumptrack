# pumptrack

Agent skills for orchestrating coding agents, so the work keeps moving with as little effort from you as possible.

A pump track is a loop of rollers and banked turns that you ride without pedaling: you keep your speed by pushing into the terrain at the right moments. pumptrack brings the same idea to agent work. The loop carries itself, and your effort goes into a few well-timed inputs.

## Status

🚧 Just started. One skill so far: `pumptrack`, an orchestrator that talks and plans with you while subagents do the work.

## Install

Ask an agent in your project to clone this repo and copy its `skills/` folder into the project's skills folder (`.claude/skills/` for Claude Code). Then start a session with `/pumptrack`.

To pick up every change in all your projects instead, link each skill into your user skills folder: `ln -s "$PWD/skills/pumptrack" ~/.claude/skills/pumptrack`.

## License

[MIT](LICENSE).
