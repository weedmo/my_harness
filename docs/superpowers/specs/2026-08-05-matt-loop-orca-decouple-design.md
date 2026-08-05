# matt-loop: decouple matt skills from Orca

**Date:** 2026-08-05
**Status:** approved

## Problem

`matt-orchestrator` (weedmo-authored) is written entirely against the Orca CLI
and its orchestration runtime (executable resolution, `skills get orchestration`,
injected dispatches, `worker_done`/`escalation`/`decision_gate` protocol).
`matt-interview` hands off to it. The matt-loop plugin is distributed for both
Claude and Codex, so its skills must not depend on Orca being installed.

## Decision

Platform-neutralize `matt-orchestrator`: keep the orchestration *structure*
(4-stage DAG, ambiguity gates, matt-interview reentry, supervision loop) and
replace the *execution mechanism* with "the platform's native parallel
subagent/task facility". No new CLI is hardcoded.

## Changes

1. `skills/matt-orchestrator/SKILL.md`
   - Frontmatter description: drop "Orca".
   - Delete the "Load the live orchestration contract" section (Orca executable
     resolution, `skills get orchestration`, `status --json`); replace with a
     short section: use the platform's native parallel subagent/task facility,
     coordinator stays in the main session, never fake parallelism, fall back
     to sequential stages when no parallel facility exists.
   - Replace Orca task/terminal/injected-dispatch mechanics with neutral
     dispatch wording (tasks with dependencies, self-contained worker prompts,
     collect final reports).
   - Worker prompt template: "Follow the injected Orca lifecycle preamble and
     report worker_done exactly once" → single final structured report.
   - `worker_done`/`escalation`/`decision_gate` waiting protocol → abstract
     coordinator supervision (wait for worker reports, classify escalations,
     create user decision gates).
   - DAG stages, ambiguity gates, and matt-interview reentry logic unchanged.
2. `skills/matt-orchestrator/references/routing.md` — "Orca role" column →
   "Worker role"; "Orca tasks" wording neutralized.
3. `skills/matt-orchestrator/agents/openai.yaml` — "parallel Orca workers" /
   "supervised Orca task DAG" neutralized.
4. `README.md` — matt-orchestrator description line neutralized.
5. `.codex-plugin/plugin.json` — `longDescription` neutralized.

## Non-changes

- Vendored mattpocock skills (overwritten by daily upstream sync).
- `matt-interview/SKILL.md` (no Orca references; the pending spec-checkpoint
  working-tree edit stays as-is and is not part of this change).

## Acceptance

`grep -ri orca plugins/matt-loop` returns zero matches.
