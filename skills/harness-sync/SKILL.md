---
name: harness-sync
description: Sync the local ~/.claude/ config (hooks, skills, agents, CLAUDE.md, settings.json, hud, scripts) to the ~/autofree/ git repo, patch-bump the version, commit, tag, push, create a GitHub Release, and refresh the local plugin cache. Use when the user says "sync", "sync harness", "publish harness", or wants to release a new patch of weed-harness.
---

# Harness Sync

Publish local `~/.claude/` config changes to the `~/autofree/` git repo, cut a patch release, and refresh the local plugin cache so this machine actually runs the version just published.

## Scope

Source: `~/.claude/` (local active config)
Target: `~/autofree/` (this git repo)

**Sync targets (repo-owned files only):**
- `hooks/` — all `.sh` files and `hooks.json`
- `skills/` — only directories already present in repo (do NOT import skills from other plugins like gstack, omc, everything-claude-code, etc.)
- `agents/` — all files
- `CLAUDE.md` — the OMC + weed-harness section (between `<!-- OMC:START -->` and the end of file)
- `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`
- `settings.json` — local active settings (statusLine, env, hooks, permissions). ALWAYS include unconditionally.
- `hud/` — all files (statusLine HUD scripts referenced by settings.json)

**Excluded:** `settings.local.json` (project-private overrides), `plugins/`, `sessions/`, `cache/`, `history.jsonl`, `projects/`, and any other runtime/state files.

## Steps

1. **Diff** — For each sync target, run `diff` between local and repo. Show a summary of changed/added/removed files. If no changes found, stop and report "Already in sync."

2. **Confirm** — Show the diff summary and proceed (do not ask for permission per auto-fix rule).

3. **Copy changes** — Update repo files from local. For new skills directories in repo that don't exist locally, keep them (repo-only files are preserved).

4. **Version bump** — Always patch bump:
   - Read current version from `.claude-plugin/plugin.json`
   - Increment patch (e.g., `2.0.1` → `2.0.2`)
   - Update all 3 locations:
     - `.claude-plugin/plugin.json` → `"version"`
     - `.claude-plugin/marketplace.json` → top-level `"version"`
     - `.claude-plugin/marketplace.json` → `plugins[0].version`

5. **Commit & Push**:
   ```
   git add -A
   git commit -m "chore: bump version to X.Y.Z"
   git tag vX.Y.Z
   git push origin main
   git push origin vX.Y.Z
   ```

6. **GitHub Release**:
   ```
   gh release create vX.Y.Z --generate-notes
   ```

7. **Local plugin update** — Pull the new release into the local Claude Code plugin cache so this machine actually runs the version just published:
   ```bash
   MARKETPLACE_DIR=~/.claude/plugins/marketplaces/weed-plugins
   # Ensure remote URL is current (repo was renamed my_harness → autofree → skills)
   git -C "$MARKETPLACE_DIR" remote set-url origin https://github.com/weedmo/skills.git
   git -C "$MARKETPLACE_DIR" fetch origin --tags
   git -C "$MARKETPLACE_DIR" reset --hard origin/main

   # Refresh plugin cache to new version
   CACHE_BASE=~/.claude/plugins/cache/weed-plugins/weed-harness
   rm -rf "$CACHE_BASE"/*/
   mkdir -p "$CACHE_BASE/X.Y.Z"
   rsync -a --exclude='.git' --exclude='plugins/' --exclude='node_modules/' "$MARKETPLACE_DIR/" "$CACHE_BASE/X.Y.Z/"

   # Update installed_plugins.json (use Python to keep JSON valid)
   python3 - <<'PY'
   import json, datetime, pathlib
   p = pathlib.Path.home() / ".claude/plugins/installed_plugins.json"
   data = json.loads(p.read_text())
   entry = data["plugins"]["weed-harness@weed-plugins"][0]
   entry["version"] = "X.Y.Z"
   entry["installPath"] = f"/home/weed/.claude/plugins/cache/weed-plugins/weed-harness/X.Y.Z"
   entry["lastUpdated"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
   import subprocess
   entry["gitCommitSha"] = subprocess.check_output(["git","-C",str(pathlib.Path.home()/".claude/plugins/marketplaces/weed-plugins"),"rev-parse","HEAD"]).decode().strip()
   p.write_text(json.dumps(data, indent=2))
   PY
   ```

8. **Verify** — Confirm ALL of:
   - Tag `vX.Y.Z` exists on GitHub (`gh release view vX.Y.Z --repo weedmo/skills`)
   - Marketplace clone HEAD matches origin/main
   - Cache dir `~/.claude/plugins/cache/weed-plugins/weed-harness/X.Y.Z/` exists with `.claude-plugin/plugin.json` showing version X.Y.Z
   - `installed_plugins.json` entry for `weed-harness@weed-plugins` shows `"version": "X.Y.Z"` and matching `installPath`

   Note: a Claude Code restart is required for skills/hooks/agents from the new version to be loaded. Report this in the final summary.
