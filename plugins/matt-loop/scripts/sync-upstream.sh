#!/usr/bin/env bash
# Sync vendored Matt Pocock skills from mattpocock/skills into this plugin.
#
# Usage: sync-upstream.sh [upstream-checkout-dir]
#   Without an argument, clones a fresh shallow copy of the upstream repo.
#
# Only the skills listed in SKILLS are managed. matt-auto, pr-babysit, and the
# routed resolving-merge-conflicts fork are weedmo-authored and never touched.
# The upstream commit is recorded in mattpocock.lock.json for provenance.
set -euo pipefail

REPO_URL="https://github.com/mattpocock/skills.git"
PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$PLUGIN_DIR/skills"
LOCK="$PLUGIN_DIR/mattpocock.lock.json"
PY="$(command -v python3 || command -v python)"

# The skills matt-auto's flow (ask-matt's main flow) drives, plus standalone
# skills kept for direct use. qa and request-refactor-plan live under
# skills/deprecated/ upstream but are kept for direct invocation.
SKILLS=(
  ask-matt
  codebase-design
  code-review
  diagnosing-bugs
  domain-modeling
  grill-me
  grill-with-docs
  grilling
  handoff
  implement
  prototype
  qa
  request-refactor-plan
  research
  setup-matt-pocock-skills
  tdd
  to-spec
  to-tickets
)

UPSTREAM="${1:-}"
CLEANUP=""
if [ -z "$UPSTREAM" ]; then
  CLEANUP="$(mktemp -d)"
  UPSTREAM="$CLEANUP/mattpocock-skills"
  git clone --depth 1 --quiet "$REPO_URL" "$UPSTREAM"
fi
trap '[ -n "$CLEANUP" ] && rm -rf "$CLEANUP"' EXIT

COMMIT="$(git -C "$UPSTREAM" rev-parse HEAD)"
missing=0
synced=()
for s in "${SKILLS[@]}"; do
  src=""
  for cat in "$UPSTREAM"/skills/*/; do
    [ -d "$cat$s" ] && src="$cat$s" && break
  done
  if [ -z "$src" ]; then
    echo "WARN: skill '$s' not found upstream - left as-is" >&2
    missing=1
    continue
  fi
  rm -rf "${DEST:?}/$s"
  cp -r "$src" "$DEST/$s"
  synced+=("$s")
done

"$PY" - "$LOCK" "$REPO_URL" "$COMMIT" "${synced[@]}" <<'EOF'
import json, sys
lock, repo, commit, skills = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
with open(lock, "w") as f:
    json.dump({"repo": repo, "commit": commit, "skills": skills}, f, indent=2)
    f.write("\n")
EOF

echo "Synced ${#synced[@]} skills from mattpocock/skills @ ${COMMIT:0:12}"
[ "$missing" -eq 0 ] || exit 3
