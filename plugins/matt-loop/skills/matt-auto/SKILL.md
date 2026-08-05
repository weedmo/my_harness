---
name: matt-auto
description: Use when the user explicitly invokes matt-auto to take an idea through Matt Pocock's full engineering flow — interview, spec, tickets, implementation — pausing only where a human decision is required.
disable-model-invocation: true
---

# Matt Auto

Drive Matt Pocock's main flow (idea → ship) end to end. You are a conductor, not a methodology: every stage is one of the vendored Matt skills, invoked as written. Automate the transitions between skills; never automate the user's decisions.

## Rules

- Invoke each stage's skill and follow it exactly. Do not reimplement, merge, or "improve" a stage.
- Wherever a sub-skill asks the user something — interview questions, seam check, ticket approval — stop and wait for the real answer. Never answer on the user's behalf.
- Discoverable facts are yours to look up; decisions are the user's. This is grilling's rule, and it governs every stage.
- Do not add gates, scores, artifacts, or orchestration the vendored skills don't define. The only artifacts are theirs: `CONTEXT.md`/ADRs, the spec on the tracker, and tickets.

## Pipeline

1. **Precondition** — if `docs/agents/issue-tracker.md` is missing, run `$setup-matt-pocock-skills` first.
2. **Interview (human-in-the-loop)** — `$grill-with-docs` in a codebase, `$grill-me` otherwise. One question at a time with a recommended answer, until the user confirms shared understanding. If a question needs a runnable answer, detour via `$prototype` and fold what you learned back into the interview.
3. **Size branch** — fits one session? Run `$implement` right here (it drives `$tdd`, then `$code-review`, then commits) and finish. Otherwise continue.
4. **Spec** — `$to-spec`, including its own seam check with the user.
5. **Tickets (human-in-the-loop)** — `$to-tickets`: present the breakdown, iterate until the user approves, then publish to the configured tracker.
6. **Implement loop** — work the frontier: pick a ticket whose blockers are all done and dispatch it to a fresh-context subagent whose prompt is "read ticket <ref>, then use $implement to build it; report open decisions back instead of guessing". One ticket at a time. If the platform has no subagents, ask the user to run `$implement` per ticket in fresh sessions and stop there.
7. Repeat step 6 until no tickets remain, then report: tickets completed, commits made, verification results, and anything escalated along the way.

## Escalation

When any stage surfaces a material decision — behavior, scope, public interfaces, data meaning or migration, security, anything destructive — pause the pipeline and ask the user, then resume where you left off. Never convert an open decision into an assumption to keep the pipeline moving.

## Red flags — you are drifting off the flow

- Scoring ambiguity percentages or inventing readiness gates → no Matt skill does this. Drop it.
- Writing specs or notes outside the tracker and `CONTEXT.md`/ADRs → wrong artifact system.
- Running several implementation workers in parallel → Matt's loop is one ticket per fresh context.
- Skipping a sub-skill's user check "to keep things moving" → that check is the point of the flow.
