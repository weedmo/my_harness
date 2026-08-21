# weed-plugins

One repo, per-loop plugins. An AI-CLI harness by weedmo — installable skill packs
for **Claude Code, Codex, opencode, and gemini-cli**.

| Plugin | Where | What | Required |
|--------|-------|------|----------|
| `weed-harness` | repo root | Claude Code-only setup, hooks, and HUD | Claude Code only |
| `matt-loop` | `plugins/matt-loop/` | matt-auto + vendored Matt Pocock skills (human-in-the-loop conducted Matt flow) | optional |
| `auto-loop` | `plugins/auto-loop/` | autocode + auto_research autonomous improvement loops | optional |

External loops (superpowers, graphify, …) are referenced, not vendored. The
`auto-update.sh` SessionStart hook keeps required skills (graphify claude/codex,
superpowers, matt-*) up to date once they are present.

## Install (recommended): npx installer

One command installs skill packs to any combination of the four supported
platforms. Claude Code receives `weed-harness` setup automatically; the loop
plugins are opt-in.

```bash
# Interactive: pick platforms, then pick plugins
npx github:weedmo/skills

# Everything, everywhere
npx github:weedmo/skills --yes

# Choose platforms and plugins explicitly
npx github:weedmo/skills --platforms claude-code,codex --plugins matt-loop,auto-loop

# Install every skill in OpenCode
npx github:weedmo/skills --platforms opencode --plugins all

# Preview without writing
npx github:weedmo/skills --yes --dry-run
```

### Where skills are installed

| Platform | Skill directory | Notes |
|----------|-----------------|-------|
| `claude-code` | `~/.claude/skills/` | Installs the Claude-only `setup` skill plus selected loop plugins. If you already installed these via `/plugin install`, skip this platform to avoid duplicates. |
| `codex` | `~/.codex/skills/` | Native SKILL.md discovery. Restart Codex after install. |
| `opencode` | `~/.config/opencode/skills/` | Native SKILL.md discovery. Invalid underscores in skill IDs are normalized to hyphens (for example, `auto_research` → `auto-research`). matt-loop also installs routing agents under `~/.config/opencode/agents/`. |
| `gemini-cli` | `~/.gemini/skills/` | No native skill discovery — reference the skill files from `~/.gemini/GEMINI.md` yourself. |

Re-running the installer overwrites installed skills with the latest versions,
so it doubles as an updater (`npx github:weedmo/skills --yes` pulls the current
main branch every time).

After installing on Claude Code, run `/setup` once to configure the statusLine
HUD and register the custom hooks (language-rule, auto-update).

## Install (alternative): native plugin systems

Every plugin is also installable through each CLI's own plugin system.

### Claude Code

```bash
/plugin marketplace add weedmo/skills

/plugin install weed-harness@weed-plugins   # Claude-only setup, hooks, and HUD
/plugin install matt-loop@weed-plugins      # optional
/plugin install auto-loop@weed-plugins      # optional
```

Or via CLI: `claude plugin marketplace add https://github.com/weedmo/skills.git`
then `claude plugin install <name>@weed-plugins`.

### Codex

```bash
codex plugin marketplace add weedmo/skills

codex plugin add matt-loop@weed-plugins      # optional
codex plugin add auto-loop@weed-plugins      # optional
```

Start a new Codex session so the packaged skills are discovered. Each package
carries `.codex-plugin/plugin.json` metadata, and the repo-local Codex
marketplace (`.agents/plugins/marketplace.json`) lists both loop plugins.

opencode and gemini-cli have no compatible plugin marketplace — use the npx
installer for those.

Current limitation: Claude-specific hook automation and slash-command behavior
ship only with the Claude plugin; on other platforms the skills act as
workflow guidance.

## Skills

### weed-harness (Claude Code only)

| Skill | Description |
|-------|-------------|
| `/setup` | Terminal UI + basic settings only: statusLine HUD, custom hooks (language-rule, auto-update) |

### matt-loop

| Skill | Description |
|-------|-------------|
| `matt-auto` | Conductor for Matt Pocock's main flow (interview → spec → tickets → implementation) with human-in-the-loop gates and automatic OpenCode model routing |
| vendored Matt Pocock skills | The upstream skills matt-auto conducts: `grilling`, `grill-me`, `grill-with-docs`, `ask-matt`, `to-spec`, `to-tickets`, `handoff`, `tdd`, `implement`, `diagnosing-bugs`, `codebase-design`, `domain-modeling`, `research`, `prototype`, `code-review`, `qa`, `request-refactor-plan`, `resolving-merge-conflicts`, `setup-matt-pocock-skills` |

The vendored skills come from
[mattpocock/skills](https://github.com/mattpocock/skills) and are auto-synced:
a daily GitHub Actions workflow (`sync-mattpocock.yml`) re-vendors them, bumps
the matt-loop patch version, and commits when upstream changed. The pinned
upstream commit lives in `plugins/matt-loop/mattpocock.lock.json`; to sync
manually, run `bash plugins/matt-loop/scripts/sync-upstream.sh`. On this
machine the `auto-update.sh` SessionStart hook then propagates every matt-loop
skill to `~/.codex/skills/`.

### auto-loop

| Skill | Description |
|-------|-------------|
| `/autocode` | Autonomous code improvement loop with optional PGE team mode |
| `/auto_research` | Autonomous ML research loop with deep-interview initialization |

## Docs

- `docs/skills-hooks-reference.html` — Notion-style reference of every skill and hook
- `docs/SKILL_MAP.md` — decision guide for picking the right skill/engine per task

## License

MIT
