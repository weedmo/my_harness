#!/usr/bin/env bash
# weed-harness setup installer.
# Idempotent: each step checks current state and only writes if needed.
#
# Usage:
#   install.sh             # install all components
#   install.sh hud         # install HUD (statusLine + hud/ copy)
#   install.sh understand  # install understand-anything plugin (codebase comprehension)
#   install.sh hooks       # register weed-harness extra hooks in settings.json
#   install.sh status      # report what is/isn't installed (no writes)
#
# Resolves plugin root from CLAUDE_PLUGIN_ROOT (set by Claude Code) or
# falls back to the directory containing this script's grandparent.

set -uo pipefail

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
USER_HOME="${HOME}"
SETTINGS="${USER_HOME}/.claude/settings.json"
USER_HUD="${USER_HOME}/.claude/hud"

# Hook commands stored in settings.json use ~/.claude/... form so they survive
# being shared across machines / different $HOME values. The script and the
# idempotence checks normalize between absolute and tilde forms.
TILDE_HOOKS_DIR='~/.claude/hooks'

# ---------- helpers ----------

log()  { printf '  %s\n' "$*"; }
ok()   { printf '  ✓ %s\n' "$*"; }
skip() { printf '  - %s (already installed)\n' "$*"; }
warn() { printf '  ! %s\n' "$*" >&2; }
err()  { printf '  ✗ %s\n' "$*" >&2; }

require_python() {
  command -v python3 >/dev/null 2>&1 || { err "python3 is required"; exit 1; }
}

ensure_settings_file() {
  if [ ! -f "$SETTINGS" ]; then
    mkdir -p "$(dirname "$SETTINGS")"
    echo '{}' > "$SETTINGS"
  fi
}

# Run a python snippet that mutates settings.json in place.
# Snippet receives `data` (parsed JSON dict) and must mutate it.
# Snippet should print "CHANGED" to stdout if it modified anything.
mutate_settings() {
  local snippet="$1"
  ensure_settings_file
  python3 - "$SETTINGS" <<PY
import json, sys, pathlib
path = pathlib.Path(sys.argv[1])
data = json.loads(path.read_text())
changed = False
def mark():
    global changed
    changed = True
${snippet}
if changed:
    path.write_text(json.dumps(data, indent=2) + "\n")
    print("CHANGED")
PY
}

# ---------- step: HUD ----------

setup_hud() {
  printf '\n[hud] statusLine HUD\n'
  local plugin_hud="${PLUGIN_ROOT}/hud/weed-hud.mjs"
  local target_hud="${USER_HUD}/weed-hud.mjs"
  local target_cmd="node ${target_hud}"

  if [ ! -f "$plugin_hud" ]; then
    err "plugin HUD not found at $plugin_hud"
    return 1
  fi

  mkdir -p "$USER_HUD"
  if [ ! -f "$target_hud" ] || ! cmp -s "$plugin_hud" "$target_hud"; then
    cp "$plugin_hud" "$target_hud"
    ok "copied HUD → $target_hud"
  else
    skip "HUD up to date at $target_hud"
  fi

  # Register statusLine in settings.json
  local result
  result=$(mutate_settings "
existing = data.get('statusLine')
desired = {'type': 'command', 'command': '${target_cmd}'}
if existing != desired:
    data['statusLine'] = desired
    mark()
")
  if [ "$result" = "CHANGED" ]; then
    ok "statusLine registered in settings.json"
  else
    skip "statusLine already configured"
  fi
}

# ---------- step: understand-anything ----------

setup_understand() {
  printf '\n[understand] understand-anything plugin (codebase comprehension)\n'
  if ! command -v claude >/dev/null 2>&1; then
    warn "claude CLI not found — skipping understand-anything install (install manually later)"
    return 0
  fi
  if claude plugin marketplace list 2>/dev/null | grep -q "understand-anything"; then
    skip "marketplace understand-anything already added"
  else
    log "adding marketplace Lum1104/Understand-Anything..."
    claude plugin marketplace add Lum1104/Understand-Anything 2>&1 | sed 's/^/    /' || warn "marketplace add failed (may already exist)"
  fi
  if claude plugin list 2>/dev/null | grep -q "understand-anything@understand-anything"; then
    skip "understand-anything@understand-anything already installed"
  else
    log "installing understand-anything..."
    claude plugin install understand-anything 2>&1 | sed 's/^/    /' || warn "install failed"
  fi
}

# ---------- step: extra hooks ----------

setup_hooks() {
  printf '\n[hooks] register weed-harness user-level hooks\n'

  # Each entry: event matcher script_basename
  # matcher empty (-) means no matcher
  local entries=(
    "UserPromptSubmit - language-rule.sh"
  )

  for entry in "${entries[@]}"; do
    set -- $entry
    local event="$1" matcher="$2" script="$3"
    local abs_script_path="${USER_HOME}/.claude/hooks/${script}"
    local plugin_script="${PLUGIN_ROOT}/hooks/${script}"

    if [ ! -f "$abs_script_path" ] && [ -f "$plugin_script" ]; then
      mkdir -p "$(dirname "$abs_script_path")"
      cp "$plugin_script" "$abs_script_path"
      chmod +x "$abs_script_path"
    fi

    local cmd="bash ${TILDE_HOOKS_DIR}/${script}"
    local matcher_py
    if [ "$matcher" = "-" ]; then
      matcher_py="None"
    else
      matcher_py="'${matcher}'"
    fi

    local result
    result=$(mutate_settings "
import os
def normalize(c):
    home = os.path.expanduser('~')
    return c.replace(home + '/.claude/', '~/.claude/') if c else c

hooks = data.setdefault('hooks', {})
groups = hooks.setdefault('${event}', [])
matcher = ${matcher_py}
cmd = '${cmd}'
script_basename = '${script}'
# Find a group with the same matcher
target = None
for g in groups:
    if g.get('matcher') == matcher or (matcher is None and 'matcher' not in g):
        target = g
        break
if target is None:
    new_group = {'hooks': [{'type': 'command', 'command': cmd}]}
    if matcher is not None:
        new_group['matcher'] = matcher
    groups.append(new_group)
    mark()
else:
    # Match by script basename so /home/weed/.../foo.sh and ~/.claude/hooks/foo.sh
    # are considered the same hook
    already = any(script_basename in normalize(h.get('command','')) for h in target.get('hooks', []))
    if not already:
        target.setdefault('hooks', []).append({'type': 'command', 'command': cmd})
        mark()
")
    if [ "$result" = "CHANGED" ]; then
      ok "registered ${event}/${matcher}: ${script}"
    else
      skip "${event}/${matcher}: ${script}"
    fi
  done
}

# ---------- status ----------

status() {
  printf '\nweed-harness setup status\n'
  printf '  PLUGIN_ROOT: %s\n' "$PLUGIN_ROOT"
  printf '  SETTINGS:    %s\n' "$SETTINGS"
  printf '\n[hud]\n'
  if [ -f "${USER_HUD}/weed-hud.mjs" ]; then ok "hud/weed-hud.mjs present"; else warn "hud/weed-hud.mjs MISSING"; fi
  python3 -c "
import json
try:
    d=json.load(open('$SETTINGS'))
    sl=d.get('statusLine')
    print('  ' + ('✓ statusLine: ' + sl.get('command','?') if sl else '! statusLine NOT configured'))
except Exception as e:
    print('  ! could not read settings.json:', e)
"
  printf '\n[understand]\n'
  if command -v claude >/dev/null 2>&1; then
    if claude plugin list 2>/dev/null | grep -q understand-anything@understand-anything; then ok "understand-anything plugin installed"; else warn "understand-anything plugin NOT installed"; fi
  else
    warn "claude CLI not available — cannot check"
  fi
  printf '\n[hooks]\n'
  for s in language-rule.sh; do
    if grep -q "$s" "$SETTINGS" 2>/dev/null; then ok "$s registered"; else warn "$s NOT registered"; fi
  done
}

# ---------- main ----------

require_python

cmd="${1:-all}"
case "$cmd" in
  all)
    setup_hud
    setup_understand
    setup_hooks
    printf '\nDone. Restart Claude Code to apply hooks/statusLine changes.\n'
    ;;
  hud)        setup_hud ;;
  understand) setup_understand ;;
  hooks)      setup_hooks ;;
  status)     status ;;
  *)
    err "Unknown command: $cmd"
    printf 'Usage: %s [all|hud|understand|hooks|status]\n' "$(basename "$0")"
    exit 1
    ;;
esac
