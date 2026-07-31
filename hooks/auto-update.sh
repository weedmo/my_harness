#!/usr/bin/env bash
# SessionStart hook: keep required skills auto-updated.
#  - graphifyy (pip): when PyPI has a newer version, upgrade and re-install
#    the graphify skill for BOTH platforms (claude + codex).
#  - superpowers plugin: best-effort `claude plugin update`.
#  - matt-* codex skills: re-sync from the weed-plugins marketplace clone.
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

# --- matt-* skills for codex: re-sync from marketplace clone when changed ---
SRC="$HOME/.claude/plugins/marketplaces/weed-plugins/plugins/matt-loop/skills"
DST="$HOME/.codex/skills"
if [ -d "$DST" ]; then
  for s in matt-interview matt-orchestrator; do
    if [ -d "$SRC/$s" ] && ! diff -rq "$SRC/$s" "$DST/$s" >/dev/null 2>&1; then
      rm -rf "${DST:?}/$s"
      cp -r "$SRC/$s" "$DST/$s"
      echo "[auto-update] codex skill $s refreshed"
    fi
  done
fi

exit 0
