---
name: matt-auto
description: Use when the user explicitly invokes matt-auto to take an already-discussed idea through Matt Pocock's full engineering flow — interview, spec, tickets, implementation. A high-effort decision delegate answers implementation-level questions on the user's behalf; the human picks the delegate's effort upfront and confirms once before tickets publish. Material decisions still escalate immediately. Invoke with `--yolo` to skip the effort question and the pre-publish confirm and run unattended to completion — escalation still pauses for material decisions, and every delegate decision is logged to a file.
disable-model-invocation: true
---

# Matt Auto

Drive Matt Pocock's main flow (idea → ship) end to end. You are a conductor, not a methodology: every stage is one of the vendored Matt skills, invoked as written.

The user settles the big frame in ordinary conversation *before* invoking this skill. By the time matt-auto starts, the remaining questions are implementation-level — the kind where the user would almost always take the recommended answer anyway. So a **decision delegate** (a persistent subagent) answers them, and the human is consulted exactly three ways: the effort pick at the start, immediate escalation of material decisions, and one confirm before tickets publish. Invoke with `--yolo` (e.g. `/matt-auto --yolo`) for a fully unattended run — see Autonomous mode below.

## Rules

- Invoke each stage's skill and follow it exactly. Do not reimplement, merge, or "improve" a stage.
- Wherever a sub-skill puts a question to "the user" — interview questions, seam check, ticket-breakdown quiz — route it to the decision delegate, unless it is material (see Escalation).
- Discoverable facts are still looked up in the environment, never asked. This is grilling's rule; only *decisions* go to the delegate.
- Do not add gates, scores, or artifacts the vendored skills don't define. The only artifacts are theirs: `CONTEXT.md`/ADRs, the spec on the tracker, and tickets.

## Pipeline

1. **Precondition** — if `docs/agents/issue-tracker.md` is missing, run `$setup-matt-pocock-skills` first.
2. **Pick effort (human)** — ask the user which reasoning effort the delegate should run at (low / medium / high / xhigh / max; recommend **high**). This is the only upfront human input. Skip this in `--yolo` mode — default to **high** and continue.
3. **Spawn the decision delegate** — one subagent at the chosen effort, kept for the whole pipeline. Give it: a summary of the big-frame conversation so far, access to the codebase, and the delegate brief below. Keep the same delegate conversation alive across stages so its decisions stay consistent; if the platform only supports one-shot subagents, carry the running Q&A log into each new delegate call instead.
4. **Interview** — `$grill-with-docs` in a codebase, `$grill-me` otherwise, exactly as written — one question at a time with a recommended answer — but each question goes to the delegate, not the user. Record every question → decision + rationale; this log is shown to the user verbatim at confirm. If a question needs a runnable answer, detour via `$prototype` and fold what you learned back in.
5. **Size branch** — fits one session? Present the interview log to the user for confirm (the small path's only gate, since it produces no tickets), then run `$implement` right here (it drives `$tdd`, then `$code-review`, then commits) and finish. Otherwise continue. In `--yolo` mode, skip this confirm too: write the interview log to the decision log and go straight to `$implement`.
6. **Spec** — `$to-spec`, its seam check answered by the delegate. to-spec publishes the spec as written; if the later confirm changes decisions, update the published spec.
7. **Tickets** — `$to-tickets`: run its breakdown quiz (granularity, blocking edges, merge/split) with the delegate and iterate to approval, but **hold publication** until step 8.
8. **Confirm (human, once)** — present the confirm package:
   - the interview Q&A log (question → decision + one-line rationale),
   - decisions that were escalated, with the user's answers,
   - the spec (tracker reference),
   - the ticket breakdown (title / blocked-by / what it delivers).
   On approval, publish the tickets per to-tickets. On change requests, rework from the affected stage with the delegate and re-confirm. Skip this step entirely in `--yolo` mode: publish the tickets per to-tickets as soon as step 7's breakdown is approved by the delegate, and write the confirm package to the decision log instead of presenting it.
9. **Implement loop** — work the frontier: pick a ticket whose blockers are all done and dispatch it to a fresh-context subagent whose prompt is "read ticket <ref>, then use $implement to build it; report open decisions back instead of guessing". One ticket at a time. Repeat until no tickets remain, then report: tickets completed, commits made, verification results, and everything the delegate decided or escalated along the way.

## Delegate brief

Include this in the delegate's prompt:

- You answer implementation-level questions on the user's behalf with senior-engineer judgment. Prefer the asker's recommended answer unless you see a concrete flaw in it.
- Reply with the decision plus a one-line rationale. Your log is shown to the user verbatim, so make each rationale legible on its own.
- Never decide these yourself; reply `ESCALATE: <why>` instead — security, data meaning or migration, destructive operations, externally visible interface changes, or anything that contradicts the big-frame summary you were given.

## Escalation

When the delegate replies `ESCALATE` — or any stage itself surfaces a material decision — pause the pipeline, put the question to the real user with a recommended answer, feed their answer back to the delegate, and resume where you left off. Never convert an open decision into an assumption to keep the pipeline moving.

## Autonomous mode (`--yolo`)

Invoke as `/matt-auto --yolo` to run the whole pipeline unattended, start to finish, in one sitting.

- **Step 2 (effort pick)** — skip; default to **high**.
- **Step 8 (confirm)** — skip; publish the tickets automatically once step 7's breakdown quiz is approved by the delegate.
- **Escalation is untouched.** `--yolo` removes routine questions, not the safety net. The delegate still replies `ESCALATE` for security, data meaning or migration, destructive operations, externally visible interface changes, or anything contradicting the big-frame summary it was given — and the pipeline still pauses and puts the question to the real user. `--yolo` means zero *routine* interruptions, never zero interruptions.
- **Decision log** — write every question → decision + rationale (interview, seam check, ticket-breakdown quiz, escalations and their answers, implement-loop decisions) to `docs/agents/matt-auto-log/<slug>.md`, updated as the pipeline runs rather than assembled at the end. With no live confirm to surface this, the file is the only record — keep it complete and legible on its own. Report its path in the final report, and whenever asked.

## Fallback

- Platform without subagents: run the flow human-in-the-loop instead — every sub-skill question goes to the user directly, and step 8's confirm is simply to-tickets' own approval. `--yolo` has no effect here; there is no delegate to run unattended.
- Delegate lost mid-pipeline: respawn it with the Q&A log so far as context.

## Red flags — you are drifting off the flow

- Answering a sub-skill's question yourself instead of routing it to the delegate → the delegate's independent judgment is the point; you grading your own recommendations is not.
- Publishing tickets before step 8's confirm, outside `--yolo` mode → that confirm is the user's only gate over the whole design; don't take it away.
- Treating `--yolo` as license to skip escalation too → it removes the effort question and the pre-publish confirm, nothing else. A material decision still stops the pipeline and goes to the real user.
- Running `--yolo` without a decision log file, or letting it fall behind → it's the only place mid-pipeline decisions are visible when nothing is presented live.
- Asking the user mid-pipeline about non-material decisions → that is the delegate's job now; the user opted out of those questions.
- Scoring ambiguity percentages or inventing readiness gates → no Matt skill does this. Drop it.
- Writing specs or notes outside the tracker and `CONTEXT.md`/ADRs → wrong artifact system.
- Running several implementation workers in parallel → Matt's loop is one ticket per fresh context.
