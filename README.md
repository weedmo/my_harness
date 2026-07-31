# weed-harness

Productivity skills for autonomous coding, research, and development workflows, packaged for Claude Code and Codex.

## Claude Code

### Quick Install

```bash
# Add marketplace
/plugin marketplace add weedmo/skills

# Install
/plugin install weed-harness@weed-plugins
```

Or via CLI:

```bash
claude plugin marketplace add https://github.com/weedmo/skills.git
claude plugin install weed-harness@weed-plugins
```

## Codex

### Quick Setup

1. Add the marketplace:

```bash
codex plugin marketplace add weedmo/skills
```

2. Install the plugin:

```bash
codex plugin add weed-harness@weed-plugins
```

3. Start a new Codex session so the packaged skills are discovered.

The Codex package lives in `plugins/weed-harness/` and is independently installable because it carries copied `skills/` and `agents/` content inside the plugin directory.

Current limitation: Claude-specific hook automation and slash-command behavior are not part of the Codex package.

## Skills

| Skill | Description |
|-------|-------------|
| `/autocode` | Autonomous code improvement loop with optional 23-stage AutoResearchClaw pipeline |
| `/auto_research` | Autonomous ML research loop with deep-interview initialization |
| `/scout` | Fast parallel reconnaissance using Explore agents before implementation |
| `/commit` | Commit message generator |
| `/release` | Automated release workflow: version bump, tag, push, GitHub Release |
| `/pr-ready` | PR preparation workflow with test verification |
| `/test-validation` | Verify code fixes with FAIL-to-PASS pattern validation |
| `/agent-development` | Guidance for creating Claude Code agents |
| `/ecc-tools` | Skill combination advisor for document-skills workflows |

## Claude Configuration

Enable the plugin in `~/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "weed-harness@weed-plugins": true
  }
}
```

## Claude Updates

```bash
/plugin marketplace update weed-plugins
/plugin update weed-harness@weed-plugins
```

## License

MIT
