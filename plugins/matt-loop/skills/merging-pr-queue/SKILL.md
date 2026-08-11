---
name: merging-pr-queue
description: Use when the user hands you a queue of already-open PRs (numbers, plus the branch they land on) and wants them merged cleanly. Most PR queues turn painful because each merge moves the target branch out from under everyone still waiting, so what should be one sitting becomes merge, conflict, merge, conflict, on repeat. This skill preps every PR in parallel using isolated git worktrees, then lands them one at a time, re-checking each against the moving target right before it merges. Trigger on "merge these PRs", "clear the PR queue", requests to batch-merge or untangle a stack of conflicting PRs, or a plain list of PR numbers plus a target branch — even without the words "skill" or "queue".
---

# Merging a PR Queue

Land a user-ordered list of open GitHub PRs onto one target branch without the usual merge → conflict → merge → conflict slog. The trick is separating what's safe to parallelize (each PR's own conflict resolution and checks) from what has to stay serial (actually touching the shared target branch, which moves after every merge).

## Rules

- Resolve conflicts with `$resolving-merge-conflicts` — same primitive, same "never abort" discipline — with one addition: a *material* clash (see Escalation) stops and asks the real user instead of being resolved blind.
- The queue order the user gave you is theirs to set, not yours to optimize. Keep it.
- The only hard-to-reverse step is landing on the shared target branch. Batch everything else behind one confirm before that happens.
- A pre-existing red CI check isn't yours to fix — only ones that turn red because of your rebase are in scope.

## Inputs

From the user (ask if either is missing):
- **PR numbers, in landing order.**
- **Target branch** — usually each PR's own declared base on GitHub; confirm if they disagree or the user names a different one.

## Pipeline

1. **Snapshot the target** — `git fetch`, note the target branch's current tip. Every PR preps against this same snapshot in step 2, so their parallel work doesn't collide.

2. **Parallel prep** — for each PR, in its own `git worktree` (one per PR — this is what makes the parallelism safe: no two PRs share a working tree):
   - `gh pr checkout <n>` into the worktree.
   - Rebase the PR branch onto the step-1 snapshot tip.
   - Conflict → `$resolving-merge-conflicts`, except pause and escalate instead of resolving if the clash is material.
   - Discover and run the project's checks (typecheck, then tests, then format — same discovery `$resolving-merge-conflicts` step 4 already does).
   - Push the rebased branch back to the PR (force-with-lease — it's the PR's own branch, not the target, so this is the normal way to land a rebase-based conflict fix).
   - `gh pr checks <n> --watch` and wait for CI. If a check is red exactly as it was before you touched the branch, leave it; if your rebase turned it red, fix it before moving on.
   - Record per PR: conflicts hit and how each was resolved (one line each), final check/CI result.

   Dispatch all PRs' prep at once — they're isolated worktrees against a read-only snapshot, so nothing here needs to wait on anything else.

3. **Confirm (human, once)** — before touching the target branch, show the plan: landing order, one line per PR (clean / conflicts resolved + list / escalated), CI status per PR. Wait for approval.

4. **Serial land** — walk the queue in the given order. For each PR:
   - Re-diff it against the target's *current* tip — not the step-1 snapshot. Earlier merges in this same run may have moved it.
   - Still clean → merge it (`gh pr merge`) and continue.
   - No longer clean — an earlier PR you just landed opened a fresh clash — re-run this one PR's prep alone (rebase onto the new tip, resolve, checks, push, wait CI) before merging it. Expect this on queues with overlapping files; it isn't a sign step 2 did anything wrong, just that the ground moved.

5. **Clean up** — remove the worktrees created in step 2.

6. **Report** — landing order actually used, every conflict and its resolution, everything escalated and how it was answered, final CI state, and the target branch's new tip.

## Escalation

A conflict is material — stop, and put it to the real user with a recommended resolution — when the two PRs' intent can't both survive: the same behavior changed in two incompatible ways, a public interface diverges between them, or resolving the hunk means guessing which PR's approach is actually correct rather than mechanically combining both. Plain textual overlap with an obvious combined result (both PRs touched nearby lines, no logic actually clashes) is yours to resolve without asking — that's most of what a real queue hits, and escalating all of it would just rebuild the exact slog this skill exists to remove.

## Red flags

- Resolving a material clash yourself because `$resolving-merge-conflicts` says never abort → that rule is about not giving up on a merge, not about skipping escalation. Both hold at once.
- Merging in step 4 before step 3's confirm → the target branch is shared; that confirm is the only gate before a hard-to-reverse action.
- Trusting step 2's prep in step 4 without rechecking against the current tip → the target moves every time a PR lands, so "clean five minutes ago" doesn't mean clean now.
- Reordering the queue "for convenience" (e.g. easiest-first) → the order encodes a decision (dependency, priority) that isn't yours to make.
- Fixing a CI check that was already red before your rebase touched the branch → out of scope; flag it, don't silently fix unrelated failures.
- Running PR preps one at a time "to be safe" → the isolated worktrees exist precisely so this doesn't need to be serial. Serialize only step 4.
