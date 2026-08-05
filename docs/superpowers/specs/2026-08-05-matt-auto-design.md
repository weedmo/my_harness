# matt-auto: human-in-the-loop conductor for Matt Pocock's main flow

**Date:** 2026-08-05
**Status:** approved

## Problem

matt-interview and matt-orchestrator replaced Matt Pocock's intended methodology
with a mashup (quantified ambiguity gates, a `.matt/` artifact system, a
parallel worker DAG) instead of driving the upstream skills as designed. The
vendored skill list also omitted main-flow links (`to-spec`, `handoff`), so
ask-matt's routed flow dead-ended.

## Decision

Replace both with a single weedmo-authored skill, `matt-auto`: a conductor that
drives ask-matt's main flow (idea → ship) end to end by invoking the vendored
skills as written, pausing only where a human decision is required.

- **Invocation:** explicit only (`disable-model-invocation: true`); the user
  runs `/matt-auto`. Individual vendored skills stay directly invocable.
- **HITL points:** interview answers (grilling), to-spec's seam check,
  to-tickets' breakdown approval, and escalations for material decisions.
  Everything else runs automatically.
- **Pipeline:** setup precondition → grill-with-docs/grill-me → size branch
  (small: `$implement` in-session) → `$to-spec` → `$to-tickets` → frontier
  implement loop, one ticket at a time in a fresh-context subagent running
  `$implement`.
- **No mashup:** no scores, no readiness gates, no `.matt/` artifacts, no
  parallel workers. Artifacts are Matt's: CONTEXT.md/ADRs, spec on the
  tracker, tickets.

## Changes

1. Add `skills/matt-auto/` (SKILL.md + agents/openai.yaml).
2. Remove `skills/matt-interview/` and `skills/matt-orchestrator/` (including
   the uncommitted spec-checkpoint edit to matt-interview).
3. `scripts/sync-upstream.sh`: add `to-spec` and `handoff` to SKILLS; re-vendor
   (triage/wayfinder/improve-codebase-architecture intentionally excluded —
   not needed by matt-auto).
4. Update descriptions: plugin README/AGENTS.md, both plugin.json files (minor
   bump to 1.2.0), marketplace.json, root README, bin/install.mjs,
   hooks/auto-update.sh, docs/SKILL_MAP.md, docs/skills-hooks-reference.html.

## Verification

- Subagent application test: with only the SKILL.md text, an agent correctly
  identified the first action, kept HITL questions under "don't bother me"
  pressure, refused parallel workers and ambiguity scoring, and escalated an
  ambiguous decision.
- `grep -ri "matt-interview\|matt-orchestrator"` returns no live references
  (dated design docs excepted).
