---
name: matt-auto
description: Use when the user explicitly invokes matt-auto to take an already-discussed idea through Matt Pocock's full engineering flow — interview, spec, tickets, implementation. A decision delegate answers implementation-level questions on the user's behalf; OpenCode routes work to task-appropriate models automatically, while other platforms retain the effort picker. Material decisions still escalate immediately. Invoke with `--yolo` to skip the pre-publish confirm and run unattended to completion, `--free` to use free-only OpenCode routing, or `--dev` / `--main` (`--pr <base>`) to also open a PR against that base and shepherd it to merge-ready.
disable-model-invocation: true
---

# Matt Auto

Drive Matt Pocock's main flow (idea → ship) end to end. You are a conductor, not a methodology: every stage is one of the vendored Matt skills, invoked as written.

The user settles the big frame in ordinary conversation *before* invoking this skill. By the time matt-auto starts, the remaining questions are implementation-level — the kind where the user would almost always take the recommended answer anyway. So a **decision delegate** (a persistent subagent) answers them, and the human is consulted for material decisions and one confirm before tickets publish. On platforms without the OpenCode routing agents, the human also picks the delegate's effort at the start. Invoke with `--yolo` (e.g. `/matt-auto --yolo`) for a fully unattended run — see Autonomous mode below. By default the run ends with commits on the working branch and **no PR**; add `--dev`, `--main`, or `--pr <base>` to also open a PR against that base and shepherd it to merge-ready — see Ship mode below.

## Rules

- Invoke each stage's skill and follow it exactly. Do not reimplement, merge, or "improve" a stage.
- Wherever a sub-skill puts a question to "the user" — interview questions, seam check, ticket-breakdown quiz — route it to the decision delegate, unless it is material (see Escalation).
- Discoverable facts are still looked up in the environment, never asked. This is grilling's rule; only *decisions* go to the delegate.
- Do not add gates or scores the vendored skills don't define. Artifacts are theirs — `CONTEXT.md`/ADRs, the spec on the tracker, and tickets — plus exactly two matt-auto reports on top: the `--yolo` decision log and the `$interview-report` HTML. Don't invent a third. The single sanctioned exception is the unlazy verification ledgers under `.unlazy/` — the per-ticket ledger (step 9) and the ship ledger (step 10) — which are working state, not reports, and exist only when the unlazy skill is installed. In ship mode the PR itself is pr-babysit's artifact, not a new matt-auto one.

## Pipeline

1. **Precondition** — if `docs/agents/issue-tracker.md` is missing, run `$setup-matt-pocock-skills` first.
2. **Select routing** — if the `matt-*` OpenCode subagent types in Model routing are available, use them automatically and do not ask for effort. If `--free` was supplied, select free-only routing. Otherwise, ask the user which reasoning effort the delegate should run at (low / medium / high / xhigh / max; recommend **high**); skip that fallback question in `--yolo` mode and use **high**.
3. **Spawn the decision delegate** — one persistent subagent for the whole pipeline. With OpenCode routing, use `matt-deep`, or `matt-free` in free-only mode. Otherwise use the effort selected in step 2. Give it: a summary of the big-frame conversation so far, access to the codebase, and the delegate brief below. Keep the same delegate conversation alive across stages so its decisions stay consistent; if the platform only supports one-shot subagents, carry the running Q&A log into each new delegate call instead.
4. **Interview** — `$grill-with-docs` in a codebase, `$grill-me` otherwise, exactly as written — one question at a time with a recommended answer — but each question goes to the delegate, not the user. Record every question → decision + rationale; this log is shown to the user verbatim at confirm. If a question needs a runnable answer, detour via `$prototype` and fold what you learned back in. Once the interview concludes, run `$interview-report` on the finished log — this applies in both default and `--yolo` mode, since both run the interview.
5. **Size branch** — fits one session? Present the interview log to the user for confirm (the small path's only gate, since it produces no tickets), then run `$implement` and finish. With OpenCode routing, classify and dispatch this implementation just like step 9; otherwise run it right here. In `--yolo` mode, skip this confirm too: write the interview log to the decision log and go straight to `$implement`. In ship mode, include the ship plan (branch → base, PR condition) in this confirm, make sure the work lands on the PR branch, and continue to step 10 after `$implement`.
6. **Spec** — `$to-spec`, its seam check answered by the delegate. to-spec publishes the spec as written; if the later confirm changes decisions, update the published spec.
7. **Tickets** — `$to-tickets`: run its breakdown quiz (granularity, blocking edges, merge/split) with the delegate and iterate to approval, but **hold publication** until step 8.
8. **Confirm (human, once)** — present the confirm package:
   - the interview Q&A log (question → decision + one-line rationale),
   - decisions that were escalated, with the user's answers,
   - the spec (tracker reference),
   - the ticket breakdown (title / blocked-by / what it delivers),
   - in ship mode, the ship plan: PR branch → base, and the PR condition (see Ship mode).
   On approval, publish the tickets per to-tickets. On change requests, rework from the affected stage with the delegate and re-confirm. Skip this step entirely in `--yolo` mode: publish the tickets per to-tickets as soon as step 7's breakdown is approved by the delegate, and write the confirm package to the decision log instead of presenting it.
9. **Implement loop** — work the frontier: pick a ticket whose blockers are all done and dispatch it to a fresh-context subagent whose prompt is "read ticket <ref>, then use $implement to build it; report open decisions back instead of guessing". With OpenCode routing, classify the ticket using Model routing and dispatch the matching agent; otherwise use the platform's normal implementation subagent. One ticket at a time. Repeat until no tickets remain, then report: tickets completed, commits made, verification results, and everything the delegate decided or escalated along the way. In ship mode, make sure every ticket lands on the PR branch (see Ship mode) and continue to step 10 instead of finishing here.

   **Per-ticket gates (when the unlazy skill is installed)** — check `~/.claude/skills/unlazy`, `~/.codex/skills/unlazy`, or `~/.agents/skills/unlazy` for `scripts/gate-check.mjs` once at loop start; skip this entirely when absent. Before dispatching a ticket, derive `.unlazy/matt-auto/<ticket>.GATES.md` from the ticket's acceptance criteria: one gate per independently required outcome, runnable (`CHECK:`/`EXPECT:`, typically the repo's own test/build commands) wherever a command can decide it, manual otherwise. Tell the subagent the ledger path defines "done" for its ticket. When the subagent returns, run `gate-check.mjs --reverify` on that ledger yourself — the subagent's own claim is not completion. Unmet gates go back to the same subagent route with the unmet ids (max 2 retries, then escalate to the user as a handoff). Mark the ticket complete only on `ALL MET`. This changes ticket *verification* only — the design stages (interview, spec, tickets, confirm) gain no new gates, and gates never replace escalation. Keep `.unlazy/` in the project's ignore rules.

10. **Ship (only with `--dev` / `--main` / `--pr <base>`)** — open the PR and shepherd it to merge-ready. Skip entirely, and mark `⏭️ no --pr`, when no base was given. Details in Ship mode below; in short: write the ship ledger (when unlazy is installed) → verify the PR condition → push the PR branch and open the PR against the base → `$pr-babysit` until merge-ready → resolve conflicts via `$resolving-merge-conflicts` and push → `--reverify` the ship ledger → report the PR URL and its measured state. Never merge.

## Progress board

Keep one pipeline board visible for the whole run so the user always sees what is happening, what the full range is, and where the run currently sits. It is the same plain markdown table on every platform (Claude Code, Codex, OpenCode) — no platform-specific UI, so the format never diverges.

Print the board as ordinary assistant output (1) when the pipeline starts, (2) at every stage transition, (3) on every escalation, and (4) in step 9 whenever a ticket changes state:

| # | Stage | Skill / route | Status |
|---|---|---|---|
| 1 | Precondition | setup-matt-pocock-skills | ✅ |
| 2 | Routing | — | ✅ |
| 3 | Delegate | matt-deep | ✅ |
| 4 | Interview | grill-with-docs → delegate | 🔄 Q7: error-handling seam |
| 5 | Size branch | — | ⏳ |
| 6 | Spec | to-spec | ⏳ |
| 7 | Tickets | to-tickets | ⏳ |
| 8 | Confirm | human | ⏳ |
| 9 | Implement loop | per-ticket routing | ⏳ |
| 10 | Ship | pr-babysit → matt-default | ⏭️ no --pr |

- Statuses: `✅` done · `🔄` in progress (append a short note of what exactly, e.g. the current interview question) · `⏳` pending · `⏭️` skipped, with why (`small path`, `--yolo`) · `⛔` waiting on an escalation answer.
- Skill / route names the vendored skill driving the stage and, once known, the routed agent (e.g. `$implement → matt-default`).
- Small path (step 5 fits one session): mark 6–9 `⏭️ small path`; the board ends at step 5, or at step 10 in ship mode.
- Step 10's note tracks the babysit cycle (e.g. `🔄 cycle 2/5: CI red`, `🔄 resolving conflict with dev`, `⛔ PR condition unmet`).

During step 9, add a ticket board under the pipeline board and update it as the frontier moves:

| Ticket | Route | Gates | Status |
|---|---|---|---|
| Add auth seam (#12) | matt-default | 3/3 | ✅ |
| Wire CLI flags (#13) | matt-fast | 1/3 | 🔄 retry 1/2 |
| Docs pass (#14) | — | — | ⏳ blocked by #13 |

- Gates is the unlazy ledger tally from the latest `--reverify` (`met/total`); `—` when unlazy is absent.
- In ship mode, step 10's note also carries the ship ledger tally from the latest `--reverify` (e.g. `🔄 gates 3/5: G4 CI red`).
- In `--yolo` mode, also append one stage-transition line per board update to the decision log so the file carries the same timeline; the board itself still prints to the terminal.

The board is display, not an artifact: never write it to its own file, and never let it stand in for a stage's own output.

## Model routing (OpenCode)

Use these installed subagent types when they are available. Classify from the actual task, not keyword matching, and use the lowest tier that is clearly sufficient:

| Route | Agent | Use when |
|---|---|---|
| Fast | `matt-fast` | Small bug fixes, type errors, focused tests, boilerplate, and mechanical edits |
| Default | `matt-default` | Ordinary feature work, tests, moderate refactors, and code-plus-doc tasks |
| Deep | `matt-deep` | Difficult debugging, architecture, broad refactors, migrations, or demanding review |
| Large context | `matt-large-context` | Repository-scale discovery or large PDF, image, video, log, or document analysis |

- Default to `matt-default` when two routes are plausible. Use `matt-deep` for the decision delegate because it makes design decisions across the whole pipeline.
- `matt-large-context` performs the broad analysis; hand any resulting focused implementation to `matt-default` or `matt-deep`.
- If `matt-large-context` cannot start because the Google provider, Gemini credentials, model, or quota is unavailable, retry the analysis with `matt-deep`. Split oversized repositories, documents, or logs into coherent chunks, ask `matt-deep` to summarize each chunk with source references, then synthesize those summaries in a final `matt-deep` call. This fallback does not require Gemini CLI. In free-only mode, use the same chunking process with `matt-free` and never cross into a paid route.
- If a fast agent reports that the task exceeds its scope, retry once with `matt-default`. If the default agent identifies a genuinely difficult reasoning problem, retry once with `matt-deep`. Do not use `xhigh` or `max` automatically.
- In `--free` mode, use `matt-free-fast` for Fast tasks and `matt-free` for every other route. Never mix paid routes into a free-only run.
- If a named routing agent is unavailable or fails because its provider/model is unavailable, fall back to the platform's normal subagent and report the fallback. Do not silently choose a different provider.

## Delegate brief

Include this in the delegate's prompt:

- You answer implementation-level questions on the user's behalf with senior-engineer judgment. Prefer the asker's recommended answer unless you see a concrete flaw in it.
- Reply with the decision plus a one-line rationale. Your log is shown to the user verbatim, so make each rationale legible on its own.
- Never decide these yourself; reply `ESCALATE: <why>` instead — security, data meaning or migration, destructive operations, externally visible interface changes, or anything that contradicts the big-frame summary you were given.

## Escalation

When the delegate replies `ESCALATE` — or any stage itself surfaces a material decision — pause the pipeline, put the question to the real user with a recommended answer, feed their answer back to the delegate, and resume where you left off. Never convert an open decision into an assumption to keep the pipeline moving.

## Autonomous mode (`--yolo`)

Invoke as `/matt-auto --yolo` to run the whole pipeline unattended, start to finish, in one sitting. `--free` may be combined with it.

- **Step 2 (routing)** — use automatic OpenCode routing when available; otherwise skip the effort pick and default to **high**.
- **Step 8 (confirm)** — skip; publish the tickets automatically once step 7's breakdown quiz is approved by the delegate.
- **Escalation is untouched.** `--yolo` removes routine questions, not the safety net. The delegate still replies `ESCALATE` for security, data meaning or migration, destructive operations, externally visible interface changes, or anything contradicting the big-frame summary it was given — and the pipeline still pauses and puts the question to the real user. `--yolo` means zero *routine* interruptions, never zero interruptions.
- **Decision log** — write every question → decision + rationale (interview, seam check, ticket-breakdown quiz, escalations and their answers, implement-loop decisions) to `docs/agents/matt-auto-log/<slug>.md`, updated as the pipeline runs rather than assembled at the end. With no live confirm to surface this, the file is the only record — keep it complete and legible on its own. Report its path in the final report, and whenever asked.

## Ship mode (`--dev` / `--main` / `--pr <base>`)

`--dev` targets `dev`, `--main` targets `main`, and `--pr <base>` targets any other base branch. Without one of these, matt-auto never opens a PR — implementation ends with commits on the working branch, exactly as before. `--yolo` and `--free` combine freely with ship mode.

- **PR branch.** Implementation must not land on the base itself. At the start of implementation (step 5 small path, or step 9), if the current branch *is* the base, create `matt-auto/<slug>` from it and check it out; if the user is already on a feature branch, keep it. The branch name is part of the ship plan shown at confirm (recommended: `matt-auto/<slug>`), and in `--yolo` mode the default is taken and written to the decision log. All `$implement` subagents commit to this branch.
- **PR condition.** The PR is opened by an agent, so the user decides *when*. The default condition is: implementation loop finished — every ticket complete with its unlazy ledger `ALL MET` (or, without unlazy, its verification passed) and nothing left escalated. If the user stated a condition anywhere in the big-frame conversation or the invocation (e.g. "open the PR only after the full test suite passes", "PR after tickets #12–#14, leave #15 for later", "not before I've seen the spec"), that condition **replaces or extends the default** — write it into the ship plan, encode it as gates in the ship ledger (below), verify it before opening the PR, and never open a PR while it is unmet. If the condition cannot be met inside this run, stop at `⛔`, report what is unmet, and hand off — do not open the PR "so far" on your own. Whether a stated condition is satisfied is never the delegate's call: it is measured, and if it is ambiguous, escalate.
- **Ship ledger (when the unlazy skill is installed).** Reuse the `gate-check.mjs` located in step 9; skip this bullet when absent. Before opening the PR, write `.unlazy/matt-auto/ship.GATES.md` with two groups of gates, runnable wherever a command can decide them:

  ```markdown
  # PR condition — must be MET before the PR is opened
  - [ ] G1: every ticket ledger is ALL MET
    CHECK: for f in .unlazy/matt-auto/*.GATES.md; do [ "$f" = .unlazy/matt-auto/ship.GATES.md ] || node <gate-check> --reverify "$f"; done
    EXPECT: ALL MET (for every ticket ledger, no UNMET)
    EVIDENCE: pending
  - [ ] G2: <one gate per user-stated PR condition, e.g. full test suite passes>
    CHECK: <the repo's own command, e.g. npm test>
    EXPECT: <pass indicator>
    EVIDENCE: pending

  # Merge-ready — must be MET before step 10 is done
  - [ ] G3: the PR exists against the requested base
    CHECK: gh pr view <branch> --json baseRefName --jq .baseRefName
    EXPECT: <base>
    EVIDENCE: pending
  - [ ] G4: every required check passes on the PR head
    CHECK: gh pr checks <pr> --required
    EXPECT: <a pass indicator from the command's output>
    EVIDENCE: pending
  - [ ] G5: GitHub reports no merge conflict
    CHECK: gh pr view <pr> --json mergeable --jq .mergeable
    EXPECT: MERGEABLE
    EVIDENCE: pending
  - [ ] G6: no reviewer is requesting changes
    CHECK: gh pr view <pr> --json reviewDecision --jq '.reviewDecision // "NONE"'
    EXPECT: (APPROVED|NONE|REVIEW_REQUIRED)
    EVIDENCE: pending
  ```

  A PR condition that no command can decide (e.g. "not before I've seen the spec") is a manual gate whose evidence is the user's explicit answer — never the delegate's. You authored these commands, so approve the ledger yourself (`gate-check.mjs --approve`). Fill `<pr>` in G4–G6 right after the PR is opened. Run `--reverify` before opening the PR (the PR-condition group must be MET; the merge-ready group is still pending), after every pr-babysit cycle, and once more before reporting. Wire failures to the existing machinery: G4 red → pr-babysit's fix cycle, G5 unmergeable → the conflict bullet below, G6 changes-requested → address the review feedback. A stop that is not merge-readiness becomes `ABANDON: <id> <reason>` in the ledger — the run ends as an honest handoff. Keep `.unlazy/` in the project's ignore rules.
- **Open the PR.** Push the PR branch to origin (plain push, never force), then open the PR against the base with `gh pr create --base <base>`. Title and body come from the spec and the tickets it delivered; link the spec/tracker reference and list the tickets. Open as a normal PR (not draft) unless the user asked otherwise.
- **Babysit.** Invoke `$pr-babysit` on the new PR exactly as written and let it drive: it watches checks, fixes PR-caused failures in an isolated worktree, and keeps its own merge-ready ledger. Its stop conditions apply unchanged (five cycles, repeated failure, external blocker, material decision) — a stop that is not merge-ready ends step 10 as an honest handoff with the PR URL and the unmet items, never as a quiet success.
- **Conflicts.** When GitHub reports the PR unmergeable (pr-babysit's G2, or `gh pr view --json mergeable`), merge the base into the PR branch in the isolated worktree — `git merge origin/<base>` — and dispatch `$resolving-merge-conflicts` with `ROUTED_EXECUTION=1` to resolve, run the project's checks, and commit. Then push the PR branch normally so GitHub re-evaluates. Do not rebase or force-push (the PR branch is shared once it is pushed), and do not resolve conflicts in the caller's original checkout. Re-check mergeability after the push; if a conflict returns because the base moved again, repeat within pr-babysit's cycle bound.
- **Merge-ready, not merged.** Step 10 is done when the PR is merge-ready — required checks green on the PR head, `mergeable == MERGEABLE`, no changes requested. With unlazy installed, that means *your own* `--reverify` on the ship ledger prints `ALL MET`; pr-babysit's merge-ready report (and its own ledger) is input, not completion. If the ship ledger disagrees with pr-babysit, the ledger wins: send the unmet ids back into another babysit cycle (within its five-cycle bound) or hand off. matt-auto never merges the PR; merging is the user's action after the report.
- **Routing.** Opening the PR is mechanical → `matt-fast`. The babysit coordinator → `matt-default` with `ROUTED_EXECUTION=1; use $pr-babysit and shepherd this PR to merge-ready` (it routes its own children: fast for status, default for normal CI fixes, deep for hard failures). Conflict resolution → `matt-deep` (`matt-free` in free-only mode; if unavailable, stop and report rather than fall back to a paid route). Without OpenCode routing, use the platform's normal subagent at the effort selected in step 2, and run conflict resolution at `high` or above.
- **Report.** Add to the final report: PR URL, base, PR condition and how it was verified, the ship ledger tally (`met/total`, or `—` without unlazy), babysit cycles run, commits pushed during babysit (including any conflict-resolution merge commits), final check state, and whether it is merge-ready. In `--yolo` mode the same goes into the decision log.

## Fallback

- Platform without subagents: run the flow human-in-the-loop instead — every sub-skill question goes to the user directly, and step 8's confirm is simply to-tickets' own approval. `--yolo` has no effect here; there is no delegate to run unattended.
- Delegate lost mid-pipeline: respawn it with the Q&A log so far as context.

## Red flags — you are drifting off the flow

- Answering a sub-skill's question yourself instead of routing it to the delegate → the delegate's independent judgment is the point; you grading your own recommendations is not.
- Publishing tickets before step 8's confirm, outside `--yolo` mode → that confirm is the user's only gate over the whole design; don't take it away.
- Treating `--yolo` as license to skip escalation too → it removes the effort question and the pre-publish confirm, nothing else. A material decision still stops the pipeline and goes to the real user.
- Running `--yolo` without a decision log file, or letting it fall behind → it's the only place mid-pipeline decisions are visible when nothing is presented live.
- Asking the user mid-pipeline about non-material decisions → that is the delegate's job now; the user opted out of those questions.
- Scoring ambiguity percentages or inventing readiness gates → no Matt skill does this. Drop it. (Step 9's per-ticket unlazy ledger is the one sanctioned exception, and it verifies implementation, never design readiness.)
- Marking a ticket complete while its unlazy ledger has unmet gates, or trusting the subagent's "done" instead of running `--reverify` → the ledger exists precisely because a confident done report is not evidence.
- Writing specs or notes outside the tracker, `CONTEXT.md`/ADRs, the `--yolo` decision log, or `$interview-report`'s output → wrong artifact system.
- Running several implementation workers in parallel → Matt's loop is one ticket per fresh context.
- Letting the progress board go stale, inventing a per-platform format for it, or writing it to a file → one uniform markdown table, reprinted at every transition, display only.
- Opening a PR without `--dev` / `--main` / `--pr <base>`, or opening it before the PR condition is measured as met → the user, not the agent, decides when a PR exists.
- Merging the PR, force-pushing the PR branch, or rebasing it to clear a conflict → merge-ready is the goal; merge the base in, resolve, push normally.
- Calling the PR merge-ready from local checks, your own reading of the checks page, or pr-babysit's "merge-ready" report while the ship ledger is not `ALL MET` → the ledger's `--reverify` against GitHub state is the evidence.
- Opening the PR while a PR-condition gate is unmet or was "met" by the delegate's say-so → PR conditions are measured, and manual ones are answered by the user.
