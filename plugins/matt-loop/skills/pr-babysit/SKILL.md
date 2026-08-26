---
name: pr-babysit
description: Use when the user wants you to babysit, watch, monitor, or shepherd one open GitHub PR until it is merge-ready by handling its checks, review feedback, and PR-caused failures. Does not merge unless explicitly requested. On OpenCode and Claude Code, direct invocation automatically routes work by complexity (model and reasoning effort).
---

# PR Babysit

Shepherd one existing PR to a merge-ready state. Watch checks, address actionable review feedback, fix failures caused by the PR, and push focused fixes to the PR branch. Do not merge unless the user explicitly asked for it.

## Merge-ready gates (unlazy)

When the [unlazy](https://github.com/Leonxlnx/unlazy) skill is installed (check `~/.claude/skills/unlazy`, `~/.codex/skills/unlazy`, or `~/.agents/skills/unlazy` for `scripts/gate-check.mjs`; skip this section when absent), "merge-ready" is a measured verdict, not your judgment. After workflow step 2, write `.unlazy/pr-babysit/<pr>.GATES.md`:

```markdown
- [ ] G1: every required check passes on the PR head
  CHECK: gh pr checks <pr> --required
  EXPECT: <a pass indicator from the command's output>
  EVIDENCE: pending

- [ ] G2: GitHub reports no merge conflict
  CHECK: gh pr view <pr> --json mergeable --jq .mergeable
  EXPECT: MERGEABLE
  EVIDENCE: pending

- [ ] G3: no reviewer is requesting changes
  CHECK: gh pr view <pr> --json reviewDecision --jq '.reviewDecision // "NONE"'
  EXPECT: (APPROVED|NONE|REVIEW_REQUIRED)
  EVIDENCE: pending
```

You authored these commands, so approve the ledger yourself (`gate-check.mjs --approve`) and run it between cycles. Wire gate failures to the existing machinery: G1 red → the fix cycle (step 5), G2 unmergeable → dispatch `$resolving-merge-conflicts` in the isolated worktree, G3 changes-requested → address the review feedback. A stop condition that is not merge-readiness (external blocker, material decision, repeated failure) becomes `ABANDON: <id> <reason>` — the run ends as an honest handoff, never as a quiet success. Report merge-ready only after `--reverify` prints `ALL MET`; unresolved-but-nonblocking review threads still go in the report as before.

## Standalone routing (OpenCode, Claude Code)

When invoked directly and the `matt-*` subagent types are available (OpenCode, or the `matt-loop:matt-*` agents on Claude Code — each fixes its own model and reasoning effort, so never add a `model` override), delegate the whole coordinator workflow to `matt-default` before inspecting or modifying the PR. In free-only mode use `matt-free`. Include the user request, repository path, PR reference, and: `ROUTED_EXECUTION=1; use $pr-babysit and shepherd this PR to merge-ready.` Wait for the routed coordinator and do not duplicate its work.

If `ROUTED_EXECUTION=1` is already present, execute the workflow and route fresh-context subtasks as follows:

| Work | Agent |
|---|---|
| Read-only status/check inspection or a mechanical fix | `matt-fast` |
| Normal CI diagnosis, review response, or focused implementation | `matt-default` |
| Difficult CI failure, semantic conflict, architecture-sensitive review | `matt-deep` |
| Very large logs or repository-wide evidence gathering | `matt-large-context` (OpenCode) or chunked `matt-max` (Claude Code), then hand the focused fix to default or deep |

Default to `matt-default` when uncertain. Escalate fast → default → deep only when the lower tier reports a concrete scope or reasoning limit. Include `ROUTED_EXECUTION=1` in every routed child prompt, especially when invoking `$resolving-merge-conflicts`, so child skills execute instead of routing recursively. In free-only mode use `matt-free-fast` for fast work and `matt-free` for everything else; if either free agent is unavailable, stop and report the blocker rather than falling back to a potentially paid model. In normal routing, unavailable named agents may fall back to the platform's normal agent if the fallback is reported.

If `matt-large-context` fails because the Google provider, Gemini credentials, model, or quota is unavailable, retry with `matt-deep`; Gemini CLI is not required. Split oversized CI logs or repository evidence into coherent chunks, preserve check names and source links in each chunk summary, and synthesize them with a final `matt-deep` call. In free-only mode use `matt-free` for this chunked fallback instead.

## Running as an Orca worker

When the prompt names an Orca task and dispatch id (matt-auto `--orca`, step 10), execute the workflow as usual with `ROUTED_EXECUTION=1`, and add the Orca lifecycle: ask blocking questions with `orca orchestration ask`, send material decisions as `escalation` messages, and finish exactly once with `orca orchestration send --type worker_done --task-id <task_id> --dispatch-id <dispatch_id> --outcome succeeded|failed` whose body carries the merge-ready ledger tally and the stop condition. A stop that is not merge-ready is `--outcome failed` with the unmet ids; never report it only in prose. The coordinator re-verifies its own ship ledger after your report.

## Workflow

1. **Identify the PR.** Use the supplied number/URL, or infer the PR for the current branch with `gh pr view`. If inference is ambiguous, ask for the PR reference.
2. **Snapshot scope.** Read the PR title, body, base/head branches and repositories, commits, changed files, reviews, unresolved review threads, and check runs. Record the base SHA so pre-existing failures can be distinguished from PR-caused failures.
3. **Isolate the PR branch.** Before any edit, create an isolated worktree checked out to the PR's actual head repository and ref. Verify the push destination from GitHub metadata, including fork ownership and write permission. Never edit, commit, or push from the caller's original branch; if the head ref cannot be checked out or pushed safely, stop and report the blocker.
4. **Classify the state.** Separate actionable items into: pending external work, mechanical fixes, normal fixes, deep fixes, large-log analysis, material decisions, and failures already present on the base branch.
5. **Work one cycle.** Dispatch independent read-only analysis in parallel. Apply only PR-scoped fixes inside the isolated worktree, follow the repository's branch and verification rules, commit focused changes, and push normally to the exact PR head ref. Never force-push unless the user explicitly authorized a rebase workflow.
6. **Watch checks.** If checks are pending, use `gh pr checks <pr> --watch` whether or not this run pushed a fix. Re-read reviews and checks when they settle; do not poll with a hand-written busy loop.
7. **Repeat with a bound.** Continue for at most five fix-and-watch cycles. Stop earlier when the PR is merge-ready or a stop condition applies.
8. **Clean up and report.** Remove the isolated worktree. Give the PR URL, commits pushed, review items addressed, final checks, remaining blockers, and whether it is merge-ready.

## Stop conditions

- **Merge-ready:** required checks pass, no unresolved actionable review feedback, and GitHub reports no merge conflict.
- **External blocker:** pending human approval, unavailable secret/infrastructure, third-party outage, or a failure already present on the base branch. Report it; do not wait forever.
- **Material decision:** security, data meaning/migration, destructive operation, public interface change, or conflicting reviewer requirements. Ask the user with a recommended answer.
- **Repeated failure:** the same failure survives two focused fixes, or five total cycles complete. Report evidence and stop instead of thrashing.

## Rules

- Do not broaden scope to unrelated red checks or opportunistic cleanup.
- Do not dismiss review feedback without a concrete rationale; report any feedback intentionally left unresolved.
- Do not approve your own PR or fabricate another reviewer's approval.
- Do not merge, close, retarget, or convert the PR to draft unless explicitly requested.
- Never claim merge-ready from local tests alone; check GitHub's current PR state. With unlazy installed, that means `--reverify` on the merge-ready ledger prints `ALL MET` — your own reading of the checks page is not evidence.
