# weed-plugins

One repo, per-loop plugins. A Claude Code / Codex harness marketplace maintained by weedmo.

| Plugin | Where | What |
|--------|-------|------|
| `weed-harness` | repo root | Core harness infra: setup, harness-sync, skill-subscribe, find-skills, workflow-plan, hooks, HUD |
| `matt-loop` | `plugins/matt-loop/` | matt-interview + matt-orchestrator (Codex-side interview → orchestrated implementation loop) |
| `auto-loop` | `plugins/auto-loop/` | autocode + auto_research autonomous improvement loops |
| `super-loop` | `plugins/super-loop/` | Superpowers-based gated development loop (brainstorm → plan → execute → verify → finish) |

External loops (superpowers, graphify, …) are referenced, not vendored: `/setup claude` installs the superpowers plugin and the graphify skill; `/setup codex` installs matt-loop skills and graphify for Codex.

## Claude Code

### Quick Install

```bash
# Add marketplace
/plugin marketplace add weedmo/skills

# Install core harness (required)
/plugin install weed-harness@weed-plugins

# Optional: loops
/plugin install auto-loop@weed-plugins
/plugin install super-loop@weed-plugins
```

Or via CLI: `claude plugin marketplace add https://github.com/weedmo/skills.git` then `claude plugin install <name>@weed-plugins`.

After installing, run `/setup` to install required skills (superpowers + graphify), the statusLine HUD, and the auto-update hook.

## Codex

### Quick Setup

1. Add the marketplace:

```bash
codex plugin marketplace add weedmo/skills
```

2. Install the matt-loop plugin:

```bash
codex plugin add matt-loop@weed-plugins
```

3. Start a new Codex session so the packaged skills are discovered.

Alternatively, `/setup codex` from Claude copies the matt-loop skills into `~/.codex/skills/` directly and the `auto-update.sh` SessionStart hook keeps them in sync.

Current limitation: Claude-specific hook automation and slash-command behavior are not part of the Codex package.

## Skills

### weed-harness (core)

| Skill | Description |
|-------|-------------|
| `/setup` | Environment bootstrap: required skills (Claude: superpowers+graphify / Codex: matt-loop+graphify), HUD, hooks |
| `/harness-sync` | "sync" — publish local config, patch-bump, tag, GitHub Release, refresh plugin cache |
| `/skill-subscribe` | Cherry-pick a single skill from an external repo and track upstream updates |
| `/find-skills` | Discover and install agent skills |
| `/workflow-plan` | Author a plan shaped for the Workflow orchestration tool |

### matt-loop (Codex)

| Skill | Description |
|-------|-------------|
| `matt-interview` | Socratic interview → execution-ready spec (≤10% ambiguity) |
| `matt-orchestrator` | Runs Matt Pocock skills via a supervised Orca task DAG |

### auto-loop

| Skill | Description |
|-------|-------------|
| `/autocode` | Autonomous code improvement loop with optional PGE team mode |
| `/auto_research` | Autonomous ML research loop with deep-interview initialization |

### super-loop

| Skill | Description |
|-------|-------------|
| `/super-loop` | Gated loop over superpowers skills: brainstorm → plan → execute → verify (loop back on failure) → finish |

## Docs

- `docs/skills-hooks-reference.html` — Notion-style reference of every skill and hook
- `docs/SKILL_MAP.md` — decision guide for picking the right skill/engine per task

## License

MIT
