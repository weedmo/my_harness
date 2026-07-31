# super-loop

Superpowers-based development loop plugin.

## What it is

A single glue skill (`super-loop`) that chains superpowers skills into one gated
loop: brainstorming → writing-plans → execution (subagent-driven / executing-plans)
→ verification-before-completion → finishing-a-development-branch, looping back to
the failing stage until verification passes.

The methodology itself is owned by the external
[superpowers](https://github.com/obra/superpowers) plugin — this package only
encodes the loop order, gates, and loop-back rules. It contains no vendored
superpowers content.

## Requirements

- superpowers plugin (`/setup claude` installs it)

## Install

```bash
/plugin install super-loop@weed-plugins
```
