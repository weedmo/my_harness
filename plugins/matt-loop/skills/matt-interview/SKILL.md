---
name: matt-interview
description: Conduct a developer-focused Socratic interview that researches the codebase, sharpens goals and requirements, quantifies implementation ambiguity, and produces an execution-ready spec before handing off to matt-orchestrator. Use when a feature, bug fix, refactor, or technical plan is underspecified; when the user asks to be interviewed, grilled, or questioned in detail; before implementation when ambiguity may exceed 10%; or when matt-orchestrator pauses and returns with new uncertainty or a spec conflict.
---

# Matt Interview

Reduce implementation ambiguity to `<= 10%`, crystallize a durable spec, then hand implementation to `$matt-orchestrator`. Never implement production code in this skill.

## Establish the lane

Classify the request as:

- **interview-only** — produce the spec and stop;
- **interview-then-implement** — hand off automatically when ready;
- **orchestrator-reentry** — revise an existing spec from new implementation evidence, then return control.

Default build, fix, and refactor requests to `interview-then-implement`. Respect an explicit request to stop after the interview.

## Preflight before questioning

Inspect applicable repository instructions, current code, tests, docs, ADRs, `CONTEXT.md`, `CONTEXT-MAP.md`, existing specs, and relevant Git state. Ask the user for decisions and judgment, not discoverable facts.

For brownfield work, capture a concise context snapshot under `.matt/context/{slug}.md`. Distinguish:

- **fact** — directly supported by code, tests, config, or primary documentation;
- **inference** — plausible but requires confirmation;
- **decision** — requires human authority because alternatives change behavior or scope.

Read [routing.md](references/routing.md) and invoke only relevant Matt skills. Use `$grilling` as the questioning discipline: ask one question at a time and provide a recommended answer. Use `$ask-matt` explicitly only when routing is unclear.

Score the preflight evidence before the first question. Initialize an unknown dimension at `0.0`; do not invent clarity. Show the provisional score and its evidence gaps at kickoff.

## Run the interview

Start with intent and desired outcome, then resolve scope and non-goals before implementation detail. After those foundations, target the weakest clarity dimension from [scoring.md](references/scoring.md).

For each round:

1. Show the round number, target dimension, and current ambiguity.
2. Ask exactly one high-leverage question.
3. Provide a developer recommendation and its principal tradeoff.
4. Wait for the user's answer.
5. Update the evidence ledger, decision ledger, breadth ledger, and score exactly once for that received answer.
6. In the next round, stay on the same thread with one pressure question—an example, counterexample, hidden assumption, boundary, or failure scenario—when it remains the highest-leverage uncertainty.

Stay on a vague answer until it becomes actionable. Challenge fuzzy terminology against repository language. When code, docs, and the user's description disagree, quote the concrete conflict and ask which behavior governs.

Complete at least one pressure pass before handoff: revisit an earlier user answer in a later round and materially sharpen an assumption, tradeoff, example, or boundary. The `pressure_pass` gate records this one minimum requirement; continue pressure-testing other answers only when it would change implementation.

Cover implementation-relevant branches only when they can change the solution:

- actors, workflows, state transitions, errors, and edge cases;
- domain terms, invariants, ownership, cardinality, and lifecycle;
- module interfaces, seams, callers, adapters, and dependencies;
- data shape, persistence, migration, compatibility, and rollback;
- security, privacy, authorization, performance, reliability, and observability;
- deployment, rollout, operational ownership, and failure recovery;
- test seams, acceptance examples, and evidence of completion;
- decisions the implementation agent may make versus decisions requiring the user.

Do not confuse exhaustive questioning with progress. Stop ordinary questioning once the quantitative and readiness gates pass.

## Score and gate

Use `scripts/score_ambiguity.py` with the rubric in [scoring.md](references/scoring.md) after each material answer.

Implementation is eligible only when all conditions hold:

- weighted ambiguity is `<= 0.10`;
- every critical dimension is at least `0.80`;
- no blocking unknown remains;
- Non-goals, Decision Boundaries, Testable Acceptance Criteria, Fact Grounding, and one Pressure Pass are complete.

If the score is below threshold but a readiness gate remains false, ask only the single closure question that resolves that named gate. If ambiguity stalls across three rounds, challenge the root assumption or simplify scope. Never silently convert an unresolved human decision into an implementation assumption.

## Crystallize the spec

Maintain the transcript at `.matt/interviews/{slug}.md` and the canonical spec at `.matt/specs/matt-interview-{slug}.md`. Follow [artifact-contract.md](references/artifact-contract.md).

The spec must contain goals, outcome, in-scope behavior, non-goals, scenarios, domain invariants, interfaces and seams, data and integration decisions, constraints, operational concerns, test seams, testable acceptance criteria, decision boundaries, resolved assumptions, non-blocking residual risks, implementation slices, and the full ambiguity breakdown.

For orchestrator reentry, append the new evidence and decision to the existing spec, increment its revision, identify invalidated tasks or acceptance criteria, and preserve history. Do not fork a competing spec.

## Hand off

For `interview-only`, report the spec path and stop.

For `interview-then-implement`, invoke `$matt-orchestrator` with the ready spec path and revision as the requirements source of truth. No additional confirmation is needed when implementation was already requested and no new external, destructive, or authority-expanding action is introduced.

For `orchestrator-reentry`, return the revised spec to the same orchestration run. Require the coordinator to compare revisions, invalidate affected tasks, rebuild dependencies, and reverify changed acceptance criteria before resuming writes.

If the user explicitly chooses to publish issues, hand the ready conversation/spec to `$to-tickets`; those external writes are not implicit.
