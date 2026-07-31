---
name: matt-orchestrator
description: Orchestrate Matt Pocock engineering skills through a supervised Orca task DAG for implementation, bug fixes, refactors, and other multi-track codebase work, pausing and returning to matt-interview when implementation ambiguity rises above 10% or invalidates readiness. Use when the user asks to implement with Matt skills, coordinate or supervise parallel agents, run skills concurrently, build a task DAG, consume a ready matt-interview spec, or combine planning, diagnosis, TDD, implementation, and review while waiting for results.
---

# Matt Orchestrator

Coordinate selected Matt skills through real Orca orchestration. Keep one coordinator responsible for the DAG, integration, and final evidence.

## Load the live orchestration contract

Resolve the Orca executable once:

- Use `ORCA_CLI_COMMAND` when set.
- Otherwise use `orca-dev` when `ORCA_DEV_REPO_ROOT` is set.
- Otherwise use `orca-ide` on Linux outside an Orca-managed terminal.
- Otherwise use `orca`.

Run `<ORCA> skills get orchestration` and read the complete output before issuing Orca commands. Follow that version-matched guide over any command examples remembered from previous sessions. If the selected executable fails, report its exact error and stop instead of trying another executable.

Confirm the runtime with `<ORCA> status --json`. Require the orchestration experimental feature. Use Orca tasks and injected dispatches; never substitute generic subagent or chat-only parallel-worker tools.

## Establish scope

Inspect repository instructions, the working tree, relevant issues or specifications, and available tests. Preserve unrelated user changes.

Translate the request into independently verifiable outcomes. Ask the user only when a missing decision materially changes behavior, architecture, external state, or destructive scope.

Use `$ask-matt` explicitly in a read-only routing task when the correct flow is unclear. Do not dispatch every Matt skill. Read [routing.md](references/routing.md) and select only skills supported by the request.

Before any write task, record the current `HEAD`, intended comparison base, merge base, and dirty-worktree state. Resolve any repository-mandated branch or base decision before dispatching edits.

When a `$matt-interview` spec is supplied, read its `matt_interview` frontmatter and use only the latest revision. Require `status: ready`, ambiguity `<= 0.10`, and completed readiness gates before dispatching writes. Record the spec path and revision on every implementation task.

When no ready spec exists and material human decisions remain, invoke `$matt-interview` before creating write tasks. Discoverable codebase facts may be investigated without reinterviewing the user.

## Build the DAG

Create a shallow DAG with no more than four stages:

1. **Discover** — Run independent read-only investigation tasks in parallel.
2. **Decide** — Synthesize evidence, resolve contradictions, and create a decision gate when user input is required.
3. **Implement** — Dispatch independent vertical slices in parallel only when their write scopes do not overlap.
4. **Verify** — Run independent tests and review axes after their implementation dependencies complete.

Keep the coordinator free to supervise. Default to at most three simultaneous workers unless the live environment or user specifies another safe limit.

For each task, record:

- one concrete outcome and acceptance check;
- explicit dependency task IDs;
- the exact `$skill-name` or skills to use;
- the requirements spec path and revision;
- read/write scope, including owned files or directories;
- whether the task is read-only, implementation, or review-only;
- required result evidence: commands, test output, findings, and modified files.

Prefer one worker owning a complete test-first vertical slice over separate workers editing the same production and test files. Serialize tasks that share generated files, migrations, lockfiles, central registries, snapshots, or public interfaces.

For `$diagnosing-bugs`, establish a tight reproduction loop before dispatching parallel hypothesis tasks. For `$tdd`, resolve and obtain any user confirmation required for the public test seam before dispatching the first write task.

Keep work in the active worktree unless the user explicitly requests a new worktree or the live Orca guide identifies a concrete isolation requirement. Parallel convenience alone is not an isolation requirement.

## Write worker prompts

Make every injected task self-contained. Use this shape:

```text
Use $<selected-skill> to deliver <outcome>.
Requirements: <matt-interview spec path>@revision <n>.
Acceptance: <observable checks>.
Scope: read <paths>; write only <paths>.
Dependencies/evidence: <inputs and required report>.
Report newly discovered unknowns and requirements conflicts separately from defects.
Do not modify unrelated files. Follow the injected Orca lifecycle preamble and report worker_done exactly once.
```

Mention skills with disabled implicit invocation explicitly, especially `$ask-matt` and `$implement`.

When a selected skill normally creates its own subagents, split its independent roles into separate Orca tasks instead. For example, dispatch the Standards and Spec axes of `$code-review` as two review-only Orca tasks. State the assigned axis in each prompt so no untracked nested orchestration is created.

## Dispatch and supervise

Create Orca tasks with dependencies, create or select one fresh agent terminal per worker in the required worktree, wait for terminal readiness, and dispatch with injection. Verify task and dispatch provenance before describing work as orchestrated.

Use `task-list --ready` to dispatch each parallel wave. Wait for `worker_done`, `escalation`, and `decision_gate` messages with bounded rolling waits. Treat a timeout as a checkpoint, not failure. Inspect task state and terminal liveness, then continue waiting while work remains active.

Accept completion only when the message payload matches the active task and dispatch. A review-only completion authorizes findings, not coordinator edits. Route fixes to an implementation owner.

Classify every reported surprise:

- **Discoverable fact** — resolve with a bounded read-only task and update task context.
- **Defect against an explicit spec** — keep ownership in the implementation/review loop.
- **Material ambiguity** — a human decision whose alternatives change behavior, scope, public interfaces, data meaning or migration, security/privacy, irreversible operations, or acceptance criteria.

Maintain an uncertainty register against the current spec revision. Re-score through `$matt-interview` when material ambiguity appears.

Do not invent a revised percentage from a prior aggregate score. Use the spec's dimension scores plus new evidence. If the breakdown is missing or any blocking unknown is present, readiness is false and reentry is required even before a precise new percentage is available.

If ambiguity rises above `0.10`, a critical clarity dimension falls below `0.80`, or a readiness gate becomes false:

1. Stop dispatching new write tasks.
2. Let unaffected running tasks finish safe work; require affected workers to checkpoint rather than guess.
3. Mark affected tasks blocked and record their IDs and evidence.
4. Set the canonical spec to `implementation-paused` and invoke `$matt-interview` in `orchestrator-reentry` mode.
5. Resume only from a newer `status: ready` revision.
6. Compare revisions, invalidate stale tasks and acceptance checks, rebuild dependencies, and then redispatch.

On escalation:

- answer a bounded worker question when existing evidence is sufficient;
- create a user decision gate when authority or intent is missing;
- redispatch after a recoverable worker failure;
- stop after the live orchestration circuit breaker or a genuinely unresolved blocker.

## Integrate and verify

After implementation tasks complete:

1. Confirm every result used the latest ready spec revision, then inspect the combined diff and check that workers stayed within ownership boundaries.
2. Dispatch repository-level tests or checks that cannot safely run per slice, using the recorded fixed point and approved base.
3. Dispatch independent Standards and Spec review tasks when `$code-review` applies.
4. Send actionable review findings to the owning implementation task or a dedicated fix task.
5. Repeat verification until acceptance checks pass or report the precise blocker.

Do not claim success from `worker_done` alone. Report the final changed files, verification commands and results, unresolved risks, and Orca task provenance.
