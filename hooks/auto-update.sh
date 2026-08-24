#!/usr/bin/env bash
# SessionStart hook: keep required skills auto-updated.
#  - graphifyy (pip): when PyPI has a newer version, upgrade and re-install
#    the graphify skill for BOTH platforms (claude + codex).
#  - superpowers plugin: best-effort `claude plugin update`.
#  - weed-plugins (claude): best-effort `claude plugin update` for the three
#    plugins installed from this repo's marketplace.
#  - weed-plugins (codex): refresh the marketplace snapshot and re-add the
#    loop plugins when they are installed natively.
#  - weed-plugins (opencode): re-run the repo installer from the marketplace
#    clone when plugin versions change (no plugin marketplace in opencode).
#  - matt-* codex skills: legacy file-sync fallback, only when the codex
#    plugins are NOT installed natively.
# Must never break session startup: all failures are swallowed, always exit 0.
set +e

PY="$(command -v python3 || command -v python)"

# --- graphify: auto-upgrade + reinstall skill for claude & codex ---
if command -v graphify >/dev/null 2>&1 && [ -n "$PY" ]; then
  installed="$("$PY" -m pip show graphifyy 2>/dev/null | awk '/^Version:/{print $2; exit}')"
  latest="$("$PY" -c "import json,urllib.request;print(json.load(urllib.request.urlopen('https://pypi.org/pypi/graphifyy/json',timeout=3))['info']['version'])" 2>/dev/null)"
  if [ -n "$installed" ] && [ -n "$latest" ] && [ "$installed" != "$latest" ]; then
    "$PY" -m pip install --user -q -U graphifyy >/dev/null 2>&1
    graphify install --platform claude >/dev/null 2>&1
    [ -d "$HOME/.codex" ] && graphify install --platform codex >/dev/null 2>&1
    echo "[auto-update] graphifyy $installed -> $latest applied (claude + codex)"
  fi
fi

# --- superpowers plugin: best-effort update (no-op if command unsupported) ---
command -v claude >/dev/null 2>&1 && claude plugin update superpowers@claude-plugins-official >/dev/null 2>&1

# --- weed-plugins (claude): keep the marketplace clone + plugin installs current ---
if command -v claude >/dev/null 2>&1 && [ -d "$HOME/.claude/plugins/marketplaces/weed-plugins" ]; then
  claude plugin marketplace update weed-plugins >/dev/null 2>&1
  for p in weed-harness matt-loop auto-loop; do
    claude plugin update "$p@weed-plugins" >/dev/null 2>&1
  done
fi

# --- weed-plugins (codex): refresh snapshot + reinstall when installed natively ---
if command -v codex >/dev/null 2>&1 && [ -d "$HOME/.codex/plugins/cache/weed-plugins" ]; then
  codex plugin marketplace upgrade weed-plugins >/dev/null 2>&1
  for p in matt-loop auto-loop; do
    codex plugin add "$p@weed-plugins" >/dev/null 2>&1
  done
fi

# --- weed-plugins (opencode): opencode has no plugin marketplace, so re-run
# the repo installer from the marketplace clone whenever plugin versions
# change. The installer handles skill-name normalization, routing agents,
# and slash commands. A version stamp keeps quiet sessions fast.
MP="$HOME/.claude/plugins/marketplaces/weed-plugins"
OC="$HOME/.config/opencode"
if [ -d "$MP" ] && [ -d "$OC" ] && command -v node >/dev/null 2>&1; then
  ver="$(node -e "const m=require('$MP/.claude-plugin/marketplace.json');console.log(m.plugins.map(p=>p.name+'@'+p.version).join(','))" 2>/dev/null)"
  stamp_file="$OC/.weed-plugins-version"
  if [ -n "$ver" ] && [ "$ver" != "$(cat "$stamp_file" 2>/dev/null)" ]; then
    if node "$MP/bin/install.mjs" --platforms opencode --plugins all >/dev/null 2>&1; then
      printf '%s\n' "$ver" > "$stamp_file"
      echo "[auto-update] opencode skills refreshed ($ver)"
    fi
  fi
fi

# --- matt-loop skills for codex: legacy file-sync fallback. Only runs when
# the codex plugins are NOT installed natively (the plugin cache path above
# supersedes this and file copies would show up as duplicates in Orca).
SRC="$HOME/.claude/plugins/marketplaces/weed-plugins/plugins/matt-loop/skills"
DST="$HOME/.codex/skills"
if [ -d "$SRC" ] && [ -d "$DST" ] && [ ! -d "$HOME/.codex/plugins/cache/weed-plugins" ]; then
  for d in "$SRC"/*/; do
    s="$(basename "$d")"
    if ! diff -rq "$d" "$DST/$s" >/dev/null 2>&1; then
      rm -rf "${DST:?}/$s"
      cp -r "$d" "$DST/$s"
      echo "[auto-update] codex skill $s refreshed"
    fi
  done
fi

exit 0
