# matt-loop (Codex package)

This directory is the Codex plugin package for the **matt loop**.

## Contents

- `.codex-plugin/plugin.json` for Codex plugin metadata
- `.claude-plugin/plugin.json` so the package is also addressable from the Claude marketplace (not installed by default)
- `skills/matt-auto` — conductor that drives Matt Pocock's main flow end to end (grilling interview → spec → tracer-bullet tickets → per-ticket implementation); a decision delegate answers implementation-level questions, material decisions escalate to the human, and the human confirms once before tickets publish; with `--dev` / `--main` / `--pr <base>` it also opens a PR against that base and shepherds it to merge-ready (pr-babysit, conflict resolution, push); with `--orca` the ticket DAG runs as parallel Orca-orchestrated workers (Run → Task → Dispatch) in separate worktrees, optionally on another connected machine, while verification and merging stay with the coordinator
- `skills/pr-babysit` — shepherds one GitHub PR through review and CI without merging it
- `skills/resolving-merge-conflicts` — routed fork of the upstream conflict-resolution skill
- Codex routing — the authored skills dispatch task tiers directly through `spawn_agent`: `gpt-5.6-luna`/low, `gpt-5.6-terra`/medium, `gpt-5.6-sol`/high, with `gpt-5.6-sol`/max reserved for retry after Deep
- `agents/` — task-tier routing agents for Claude Code (`matt-loop:matt-fast` haiku/low, `matt-default` sonnet/medium, `matt-deep` opus/high, `matt-max` fable/xhigh); each fixes model and reasoning effort, so matt-auto, pr-babysit, and resolving-merge-conflicts route by task without an effort picker
- `opencode/agents/` — task-tier agents installed only for OpenCode; authored skills route fast, ordinary, deep, large-context, and explicitly free-only work to the configured models, with chunked OpenAI fallback when Gemini is unavailable
- Remaining skill directories are vendored from [mattpocock/skills](https://github.com/mattpocock/skills) and remain directly invocable for partial work
- `mattpocock.lock.json` — pinned upstream commit and the list of vendored skills
- `scripts/sync-upstream.sh` — re-vendors the pinned skill list from upstream and refreshes the lock file
- `AGENTS.md` with Codex-specific notes

## Upstream sync

The vendored skills are managed automatically: the `sync-mattpocock.yml`
GitHub Actions workflow runs daily, re-runs `scripts/sync-upstream.sh`, and —
when upstream changed — bumps the matt-loop patch version and commits. Do not
hand-edit the vendored skill directories; changes will be overwritten on the
next sync. matt-auto, pr-babysit, and resolving-merge-conflicts are
weedmo-authored and are never touched by the sync.

## Installation

Normally you do not install this package directly: cherry-pick the skills into
`~/.codex/skills/` once, and the `auto-update.sh` SessionStart hook (registered
by `/setup hooks` in Claude Code) keeps them in sync with the marketplace clone
afterwards.

Root installation instructions live in the repository `README.md`.
