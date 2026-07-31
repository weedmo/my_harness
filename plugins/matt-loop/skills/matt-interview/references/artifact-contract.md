# Spec and reentry contract

Write one canonical Markdown spec at `.matt/specs/matt-interview-{slug}.md`.

Start it with this machine-readable frontmatter:

```yaml
---
matt_interview:
  schema_version: 1
  status: interviewing
  ambiguity: 1.0
  threshold: 0.10
  revision: 1
  lane: interview-then-implement
  source: user
  supersedes_revision: null
  invalidated_task_ids: []
  scores:
    intent: 0.0
    outcome: 0.0
    scope: 0.0
    behavior: 0.0
    domain_data: 0.0
    interfaces: 0.0
    constraints_operations: 0.0
    verification: 0.0
  gates:
    non_goals: false
    decision_boundaries: false
    acceptance_criteria: false
    fact_grounding: false
    pressure_pass: false
  blocking_unknowns: []
---
```

Allowed `status` values:

- `interviewing`
- `ready`
- `implementation-paused`
- `blocked`

Allowed `lane` values:

- `interview-only`
- `interview-then-implement`
- `orchestrator-reentry`

Set `status: ready` only when the scoring script returns `eligible_for_implementation: true`.

Treat frontmatter as the latest-state projection. Preserve the full revision chain, prior scores, decisions, and invalidations in the `Revision and Reentry Log` section.

## Required sections

1. Problem and Intent
2. Desired Outcome
3. Current-State Evidence
4. In Scope
5. Non-goals
6. Actors and Behavioral Scenarios
7. Domain Terms and Invariants
8. Interfaces, Seams, and Integrations
9. Data, Migration, and Compatibility
10. Constraints and Operations
11. Test Seams and Acceptance Criteria
12. Decision Boundaries
13. Assumptions and Resolutions
14. Residual Non-blocking Risks
15. Implementation Slices and Dependencies
16. Ambiguity Breakdown and Readiness Gates
17. Revision and Reentry Log

Write acceptance criteria as observable behavior, preferably Given/When/Then examples. Name the agreed public test seams.

## Orchestrator reentry brief

When implementation discovers a material unknown, set the spec status to `implementation-paused` and append:

- discovering task and evidence;
- exact conflict with the current spec;
- affected dimensions and provisional new scores;
- blocked or invalidated task IDs;
- smallest human decision needed;
- safe work that may continue;
- recommendation and tradeoff.

Resume the same spec through `$matt-interview`. After resolution:

- increment `revision`;
- set `supersedes_revision` to the prior revision;
- append the answer and evidence;
- update acceptance criteria and implementation slices;
- list invalidated tasks;
- recompute ambiguity and readiness;
- set `status: ready` only when all gates pass again.

The orchestrator must consume the latest ready revision and must not rely on superseded requirements.
