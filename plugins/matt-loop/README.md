# matt-loop (Codex package)

This directory is the Codex plugin package for the **matt loop**.

## Contents

- `.codex-plugin/plugin.json` for Codex plugin metadata
- `.claude-plugin/plugin.json` so the package is also addressable from the Claude marketplace (not installed by default)
- `skills/matt-interview` — Socratic interview that drives implementation ambiguity below 10% and produces an execution-ready spec
- `skills/matt-orchestrator` — runs Matt Pocock skills through a supervised Orca task DAG, returning to matt-interview when ambiguity rises
- `agents/` for packaged agent guidance
- `AGENTS.md` with Codex-specific notes

## Installation

Normally you do not install this package directly: `/setup codex` (from the
weed-harness plugin) copies these skills into `~/.codex/skills/`, and the
`auto-update.sh` SessionStart hook keeps them in sync afterwards.

Root installation instructions live in the repository `README.md`.
