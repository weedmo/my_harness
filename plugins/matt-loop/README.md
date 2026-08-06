# matt-loop (Codex package)

This directory is the Codex plugin package for the **matt loop**.

## Contents

- `.codex-plugin/plugin.json` for Codex plugin metadata
- `.claude-plugin/plugin.json` so the package is also addressable from the Claude marketplace (not installed by default)
- `skills/matt-auto` — conductor that drives Matt Pocock's main flow end to end (grilling interview → spec → tracer-bullet tickets → per-ticket implementation); a high-effort decision delegate answers implementation-level questions, material decisions escalate to the human, and the human confirms once before tickets publish
- `skills/<everything else>` — vendored Matt Pocock skills matt-auto conducts (grilling, to-spec, to-tickets, implement, code-review, ...), copied verbatim from [mattpocock/skills](https://github.com/mattpocock/skills) and still directly invocable for partial work
- `mattpocock.lock.json` — pinned upstream commit and the list of vendored skills
- `scripts/sync-upstream.sh` — re-vendors the pinned skill list from upstream and refreshes the lock file
- `agents/` for packaged agent guidance
- `AGENTS.md` with Codex-specific notes

## Upstream sync

The vendored skills are managed automatically: the `sync-mattpocock.yml`
GitHub Actions workflow runs daily, re-runs `scripts/sync-upstream.sh`, and —
when upstream changed — bumps the matt-loop patch version and commits. Do not
hand-edit the vendored skill directories; changes will be overwritten on the
next sync. matt-auto is weedmo-authored and is never touched by the sync.

## Installation

Normally you do not install this package directly: cherry-pick the skills into
`~/.codex/skills/` once, and the `auto-update.sh` SessionStart hook (registered
by `/setup hooks`) keeps them in sync with the marketplace clone afterwards.

Root installation instructions live in the repository `README.md`.
