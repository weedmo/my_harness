---
name: matt-auto
description: "Use when the user explicitly invokes matt-auto to take an already-discussed idea through Matt Pocock's full engineering flow — interview, spec, tickets, implementation. Runs unattended by default - a decision delegate answers every routine question on the user's behalf, material decisions still escalate immediately, and every decision lands in an editable decision-graph HTML report (edit or flag nodes there and matt-auto reworks from the affected stage). The one gate that always runs is the interview gate: right after the interview that report is published as an Orca artifact link and the pipeline waits for the user's go-ahead before any implementation starts. Codex, OpenCode, and Claude Code route work to task-appropriate models and reasoning efforts automatically. Invoke with `--confirm` to restore the human confirm gates (`--yolo` is accepted as a legacy no-op), `--free` to use free-only OpenCode routing, `--dev` / `--main` (`--pr <base>`) to also open a PR against that base and shepherd it to merge-ready, or `--parallel N` / `--on <env>` to override how many Orca workers run at once and where. Parallel execution is automatic: matt-auto probes Orca, plans which tickets run concurrently and which stay sequential, and shows that plan plus live progress, percentages, and an ETA in the artifact (`--orca` is accepted as a legacy no-op)."
disable-model-invocation: true
---

# Matt Auto

Drive Matt Pocock's main flow (idea → ship) end to end. You are a conductor, not a methodology: every stage is one of the vendored Matt skills, invoked as written.

The user settles the big frame in ordinary conversation *before* invoking this skill. By the time matt-auto starts, the remaining questions are implementation-level — the kind where the user would almost always take the recommended answer anyway. So a **decision delegate** (a persistent subagent) answers them, and matt-auto runs unattended by default, start to finish — see Autonomous by default below. The human is still consulted for material decisions (see Escalation), holds one mandatory look at the design right after the interview (see Interview gate below), and every decision is recorded in the decision log and rendered as an editable decision-graph HTML the user can push changes back through — see Decision-graph report below. Invoke with `--confirm` to restore the interactive gates (the live interview-log confirm and the pre-publish confirm); `--yolo` is still accepted as a legacy alias for the default and changes nothing. Codex, OpenCode, and Claude Code select the delegate's model and reasoning effort automatically. By default the run ends with commits on the working branch and **no PR**; add `--dev`, `--main`, or `--pr <base>` to also open a PR against that base and shepherd it to merge-ready — see Ship mode below. Implementation parallelism is matt-auto's own call: when Orca orchestration is reachable it plans the ticket DAG into waves and runs the independent ones concurrently as Orca workers, falling back to one-at-a-time in-session when it is not — see Parallel execution below.

## Rules

- Invoke each stage's skill and follow it exactly. Do not reimplement, merge, or "improve" a stage.
- Wherever a sub-skill puts a question to "the user" — interview questions, seam check, ticket-breakdown quiz — route it to the decision delegate, unless it is material (see Escalation).
- Discoverable facts are still looked up in the environment, never asked. This is grilling's rule; only *decisions* go to the delegate.
- Do not add gates or scores the vendored skills don't define. Artifacts are theirs — `CONTEXT.md`/ADRs, the spec on the tracker, and tickets — plus exactly two matt-auto reports on top: the decision log and the `$interview-report` decision-graph HTML (whose `<slug>.edits.json` round-trip and its Orca artifact link are part of it — the link is delivery of that same report, not a third one). Don't invent a third. The single sanctioned exception is the unlazy verification ledgers under `.unlazy/` — the per-ticket ledger (step 9) and the ship ledger (step 10) — which are working state, not reports, and exist only when the unlazy skill is installed. In ship mode the PR itself is pr-babysit's artifact, not a new matt-auto one.

## Pipeline

1. **Precondition** — record the run's baseline commit (`git rev-parse --short HEAD`) in the decision log before anything changes; the final report measures every number against it. If `docs/agents/issue-tracker.md` is missing, run `$setup-matt-pocock-skills` first. If the invoked idea already has a decision log and `docs/agents/matt-auto-log/<slug>.edits.json` exists, apply those graph edits before anything else — see Decision-graph report.
2. **Select routing** — use Model routing (the shared `$model-routing` table, mapped to matt roles below) automatically on Codex, OpenCode, and Claude Code; never ask the user to pick an effort on those platforms. Codex routes with `spawn_agent` model/effort overrides, OpenCode uses its `matt-*` subagent types, and Claude Code uses the `matt-loop:matt-*` agents. If `--free` was supplied, select free-only routing on OpenCode; on other platforms report that `--free` has no free route and continue with normal automatic routing. On any other platform with neither named routing agents nor model/effort overrides, ask which reasoning effort the delegate should run at (low / medium / high / xhigh / max; recommend **high**); in autonomous mode (the default) skip that fallback question and use **high** — ask it only with `--confirm`. Always probe Orca here (`orca status --json`, then `orca orchestration run-list --json`) — no flag needed; the result decides whether step 7's execution plan may use parallel waves. If `orca` fails with `bad option: --no-sandbox`, the shim is broken, not Orca: retry the same commands with `orca-ide` and use that binary for the rest of the run. If both fail, print `Orca unavailable: <why>` on the board, plan every wave sequential, and continue with the in-session implementation loop — never substitute another parallel mechanism. In the same probe, have `$interview-report` **probe** report delivery (it hands that to the shared `$loop-report`) and put its answer on the board (`Report delivery: link` / `tab — <why>` / `path — <why>`), so the user learns before the interview gate — not at it — when there will be no public link. Delivery is loop-report's job end to end; matt-auto never runs an `orca artifacts`, `tab`, or `reload` command itself. If the weed-harness shared skills (`$loop-report`, `$model-routing`, `$loop-gates`) are missing, say `weed-harness 3.x required: <skill> missing` once on the board and continue with the fallback each of them names.
3. **Spawn the decision delegate** — one persistent Deep-route subagent for the whole pipeline (`matt-deep`, or `matt-free` in free-only mode). Give it: a summary of the big-frame conversation so far, access to the codebase, and the delegate brief below. On Codex, spawn it with the Deep model/effort pair and `fork_turns: "none"`; the prompt's explicit big-frame summary replaces inherited conversation context and permits the model override. Keep the same delegate conversation alive across stages so its decisions stay consistent; if the platform only supports one-shot subagents, carry the running Q&A log into each new delegate call instead.
4. **Interview** — `$grill-with-docs` in a codebase, `$grill-me` otherwise, exactly as written — one question at a time with a recommended answer — but each question goes to the delegate, not the user. Record every question → decision + rationale; this log is shown to the user verbatim at confirm. If a question needs a runnable answer, detour via `$prototype` and fold what you learned back in. Once the interview concludes, run `$interview-report` on the decision log so far — in both autonomous and `--confirm` mode, since both run the interview — and then hold the **interview gate** (see below) until the user approves: the report is published as an Orca artifact link and nothing downstream starts while the gate is open.
5. **Size branch** — fits one session? By default (autonomous), write the interview log to the decision log and go straight to `$implement`; regenerate the decision-graph report when it finishes. With `--confirm`, first present the interview log to the user for confirm (the small path's only gate, since it produces no tickets). With automatic routing, classify this implementation with Model routing and run it as an **in-session** routed subagent; otherwise run it right here. Never as an Orca worker: the small path has nothing to run concurrently, and a worker's worktree, setup, dispatch, polling and merge-back added ten-plus minutes to a one-file change in testing. In ship mode, include the ship plan (branch → base, PR condition) in this confirm, make sure the work lands on the PR branch, and continue to step 10 after `$implement`.
6. **Spec** — `$to-spec`, its seam check answered by the delegate. to-spec publishes the spec as written; if the later confirm changes decisions, update the published spec.
7. **Tickets** — `$to-tickets`: run its breakdown quiz (granularity, blocking edges, merge/split) with the delegate and iterate to approval, but **hold publication** until step 8. Then **plan the execution** — waves, parallel or sequential, with an estimate per ticket (see Parallel execution) — and republish the artifact with that plan so the user can see how the run intends to proceed before it starts.
8. **Confirm (`--confirm` only; human, once)** — by default (autonomous) skip this step entirely: publish the tickets per to-tickets as soon as step 7's breakdown is approved by the delegate, and write the confirm package to the decision log instead of presenting it. With `--confirm`, present the confirm package:
   - the interview Q&A log (question → decision + one-line rationale),
   - decisions that were escalated, with the user's answers,
   - the spec (tracker reference),
   - the ticket breakdown (title / blocked-by / what it delivers),
   - in ship mode, the ship plan: PR branch → base, and the PR condition (see Ship mode),
   - the execution plan: waves (parallel / sequential with the reason), concurrency, placement, the worktree naming rule `matt-auto/<ticket>`, and each ticket's planned route → worker model/effort (see Parallel execution).
   On approval, publish the tickets per to-tickets. On change requests, rework from the affected stage with the delegate and re-confirm.
9. **Implement loop** — work the frontier: pick a ticket whose blockers are all done and dispatch it to a fresh-context subagent whose prompt is "read ticket <ref>, then use $implement to build it; report open decisions back instead of guessing". With automatic routing, classify the ticket using Model routing and dispatch the matching route; otherwise use the platform's normal implementation subagent. Follow step 7's execution plan: a sequential wave runs one ticket at a time, a parallel wave runs its tickets concurrently as Orca workers in their own worktrees (up to the plan's concurrency) and the coordinator merges finished tickets back one by one; see Parallel execution for that loop. Repeat until no tickets remain, then produce the final before → after report (see Final report below): regenerate the decision graph with its `outcome` block over the full decision log and publish it through `$interview-report` (same link or tab as the rest of the run), and report tickets completed, commits made, verification results, the link, and, when workers ran, the Run id and per-ticket dispatch ids — pointing at the graph for the decisions themselves rather than restating them as prose. In ship mode, make sure every ticket lands on the PR branch (see Ship mode) and continue to step 10 instead of finishing here.

   **Review pass (after the last ticket, before the final report)** — run `$code-review` over the whole run's diff (`<baseline>..HEAD`), not per ticket: the per-ticket gates prove each ticket did its job, this proves they add up to something worth shipping. Record each dimension it reports as a `review.passes` entry with its finding count, fix what it confirms, and re-run the affected tickets' gates. In ship mode this happens **before** the PR is opened, so the PR starts from reviewed code. The artifact shows it as the 리뷰 lane at the end of the flow — see Live board in the artifact.

   **Per-ticket gates** — follow `$loop-gates` (shared): locate unlazy once at loop start and skip gates entirely when absent; before dispatching a ticket, derive `.unlazy/matt-auto/<ticket>.GATES.md` from the ticket's acceptance criteria (one runnable gate per required outcome, `CHECK:`/`EXPECT:` from the repo's own commands, manual only where no command decides it); tell the subagent that ledger defines "done"; when it returns, run `gate-check.mjs --reverify` yourself; unmet gates go back to the same route with the unmet ids, max 2 retries, then escalate as a handoff; mark the ticket complete only on `ALL MET`. This changes ticket *verification* only — the design stages gain no gates, and gates never replace escalation. Keep `.unlazy/` ignored.

10. **Ship (only with `--dev` / `--main` / `--pr <base>`)** — open the PR and shepherd it to merge-ready. Skip entirely, and mark `⏭️ no --pr`, when no base was given. Details in Ship mode below; in short: write the ship ledger (when unlazy is installed) → verify the PR condition → push the PR branch and open the PR against the base → `$pr-babysit` until merge-ready, in-session → resolve conflicts via `$resolving-merge-conflicts` and push → `--reverify` the ship ledger → report the PR URL and its measured state. Never merge.

## Progress board

Keep one pipeline board visible for the whole run so the user always sees what is happening, what the full range is, and where the run currently sits. It is the same plain markdown table on every platform (Claude Code, Codex, OpenCode) — no platform-specific UI, so the format never diverges.

Print the board as ordinary assistant output (1) when the pipeline starts, (2) at every stage transition, (3) on every escalation, and (4) in step 9 whenever a ticket changes state:

| # | Stage | Skill / route | Status |
|---|---|---|---|
| 1 | Precondition | setup-matt-pocock-skills | ✅ |
| 2 | Routing | matt-* (+ Orca run_7c…) | ✅ |
| 3 | Delegate | matt-deep | ✅ |
| 4 | Interview | grill-with-docs → delegate | 🔄 Q7: error-handling seam |
| 5 | Size branch | — | ⏳ |
| 6 | Spec | to-spec | ⏳ |
| 7 | Tickets | to-tickets | ⏳ |
| 8 | Confirm | human | ⏳ |
| 9 | Implement loop | per-ticket routing | ⏳ |
| 9b | Review pass | `$code-review` | ⏳ |
| 10 | Ship | pr-babysit → matt-default | ⏭️ no --pr |

- Statuses: `✅` done · `🔄` in progress (append a short note of what exactly, e.g. the current interview question) · `⏳` pending · `⏭️` skipped, with why (`small path`, `autonomous`) · `⛔` waiting on an escalation answer, or on the interview gate (`⛔ interview gate`).
- Skill / route names the vendored skill driving the stage and, once known, the routed agent (e.g. `$implement → matt-default`).
- Small path (step 5 fits one session): mark 6–9 `⏭️ small path`; the board ends at step 5, or at step 10 in ship mode.
- Step 10's note tracks the babysit cycle (e.g. `🔄 cycle 2/5: CI red`, `🔄 resolving conflict with dev`, `⛔ PR condition unmet`).

During step 9, add a ticket board under the pipeline board and update it as the frontier moves:

| Ticket | Route | Worker | Gates | Status |
|---|---|---|---|---|
| Add auth seam (#12) | matt-default | d_3a1 · wt/12 | 3/3 | ✅ merged |
| Wire CLI flags (#13) | matt-fast | d_3a2 · wt/13 · vn | 1/3 | 🔄 retry 1/2 |
| Docs pass (#14) | — | — | — | ⏳ blocked by #13 |

- Worker is the Orca dispatch id, worktree, and (when remote) the environment; `—` for a ticket running in-session. For an Orca worker, Route also carries the model/effort passed to `worker-start` (e.g. `matt-default → sonnet/medium`).

- Gates is the unlazy ledger tally from the latest `--reverify` (`met/total`); `—` when unlazy is absent.
- In ship mode, step 10's note also carries the ship ledger tally from the latest `--reverify` (e.g. `🔄 gates 3/5: G4 CI red`).
- In autonomous mode (the default), also append one stage-transition line per board update to the decision log so the file carries the same timeline; the board itself still prints to the terminal.
- Every board update also republishes the artifact once tickets exist — see Live board in the artifact.

The board is display, not an artifact: never write it to its own file, and never let it stand in for a stage's own output.

## Model routing (Codex, OpenCode, Claude Code)

The tiers, the exact model/effort pair each resolves to per platform, the dispatch mechanics (`spawn_agent` overrides with `fork_turns: "none"` and `ROUTED_EXECUTION=1` on Codex, fixed-effort agents on Claude Code, packaged agents on OpenCode, `worker-start` flags for Orca), the escalation ladder, and the large-context chunking all live in the shared **`$model-routing`** skill (weed-harness). Read it; do not restate pairs here. matt-loop's roles map onto its tiers:

| matt role | Tier | Claude Code agent | Notes |
|---|---|---|---|
| `matt-fast` | Fast | `matt-loop:matt-fast` | Small fixes, boilerplate, mechanical edits, opening a PR |
| `matt-default` | Default | `matt-loop:matt-default` | Ordinary tickets, the babysit coordinator; the default when two routes are plausible |
| `matt-deep` | Deep | `matt-loop:matt-deep` | The decision delegate (design decisions across the whole run), hard tickets, conflict resolution |
| `matt-max` | Max | `matt-loop:matt-max` | Only as the retry after `matt-deep` reports the problem is beyond it |
| `matt-large-context` | Large context | chunk via `matt-max` | Gemini on OpenCode; chunked Max elsewhere |
| `matt-free` / `matt-free-fast` | free-only (OpenCode) | — | `--free` mode only; never mix a paid route in |

- Classify each ticket and each standalone task from what it actually needs, lowest clearly sufficient tier. Retry one rung up when a route reports the task is beyond it, per the ladder in `$model-routing`; on OpenCode `matt-deep` is the ceiling.
- If a named routing agent or Codex model override is unavailable, fall back to the platform's normal subagent and report the fallback. Do not silently choose a different provider or model.

## Delegate brief

Include this in the delegate's prompt:

- You answer implementation-level questions on the user's behalf with senior-engineer judgment. Prefer the asker's recommended answer unless you see a concrete flaw in it.
- Reply with the decision plus a one-line rationale. Your log is shown to the user verbatim, so make each rationale legible on its own.
- Never decide these yourself; reply `ESCALATE: <why>` instead — security, data meaning or migration, destructive operations, externally visible interface changes, or anything that contradicts the big-frame summary you were given.

## Escalation

When the delegate replies `ESCALATE` — or any stage itself surfaces a material decision — pause the pipeline, put the question to the real user with a recommended answer, feed their answer back to the delegate, and resume where you left off. Never convert an open decision into an assumption to keep the pipeline moving.

## Autonomous by default (`--confirm` to opt out)

matt-auto runs the whole pipeline unattended, start to finish, in one sitting — no flag needed (`--yolo` is still accepted as a legacy alias and changes nothing). Invoke with `--confirm` to restore the interactive gates instead. `--free` combines with either.

- **Step 2 (routing)** — use automatic routing on Codex, OpenCode, and Claude Code; otherwise skip the fallback effort pick and default to **high** (only `--confirm` asks it).
- **Steps 5 and 8 (confirms)** — skipped by default; tickets publish automatically once step 7's breakdown quiz is approved by the delegate. `--confirm` restores both gates.
- **Step 4's interview gate is never skipped** — autonomous or not, the pipeline stops there for the user's go-ahead. See Interview gate below.
- **Escalation is untouched.** Autonomous removes routine questions, not the safety net. The delegate still replies `ESCALATE` for security, data meaning or migration, destructive operations, externally visible interface changes, or anything contradicting the big-frame summary it was given — and the pipeline still pauses and puts the question to the real user. Autonomous means zero *routine* interruptions, never zero interruptions.
- **Decision log** — write every question → decision + rationale (interview, seam check, ticket-breakdown quiz, escalations and their answers, implement-loop decisions) to `docs/agents/matt-auto-log/<slug>.md`, updated as the pipeline runs rather than assembled at the end. With no live confirm to surface this, the file is the only textual record — keep it complete and legible on its own. Report its path in the final report, and whenever asked. (`--confirm` mode presents decisions live instead and keeps no log.)

## Live board in the artifact

Once tickets exist, the report stops being a snapshot and becomes the run's status page: **every board update is also a republish**. "Republish" throughout this file means one thing: hand `$interview-report` the regenerated data — `progress` + `tickets` blocks and all — and let it **publish**; it builds the page and pushes it through `$loop-report` to wherever the user is already reading it (the artifact link, or the Orca browser tab when the run has no link), keeping that route stable. The page polls itself until `progress.state` is `done`. Never skip a republish because the link is missing — the route is the report skill's problem, the timing is yours.

- **When to republish:** exactly when the board changes — a stage transition, a ticket moving to in-progress / done / blocked, a gate re-verification result, an escalation raised or answered. Not on a timer, and not per commit.
- **What "blocked" means here:** the run cannot proceed on that ticket right now — unmet gates after the retries, an escalation waiting on the user, CI red, a merge conflict, an Orca worker that stopped. Fill `blocker.reason` and put the checkable fact in `blocker.detail` (the unmet gate id and its expected-vs-actual, the failing check, the question being asked). A ticket merely waiting on its blockers is `pending` with `blockedBy`, not `blocked`.
- **`progress.current`** is one line on what is happening right now — the same note the board's `🔄` carries.
- **Every ticket node carries who is running it**: the route from Model routing, the model and effort that route resolved to, and — for a ticket running as an Orca worker — its dispatch id and worktree. The same facts the board's Worker column shows, so the artifact answers "이 티켓은 누가 어떤 모델로" without opening the terminal.
- **Percentages and ETA come from the data, not from you.** Set `progress.startedAt` once, give every ticket an `estimateMin` when you plan the waves, and stamp `startedAt` / `actualMin` as tickets begin and finish; the page derives the overall percent, the per-stage bars, 남은 예상 and 완료 예정 시각 from that. Re-estimate a ticket only when you learn something that changes it, and say so in `progress.note` — silently rewriting estimates to keep a bar moving is falsifying a report.
- **The plan is published before implementation starts** (step 7's republish) and stays through the run, so the user can see the intended shape and then watch the tickets inside it move.
- **The flow does not end at the last ticket.** Fill `review` while the review pass runs, and in ship mode fill `pr` — number, branch → base, the check rows (CI, reviewers, mergeable) with their measured state, and the babysit cycle count. They render as the 리뷰 and PR lanes at the right end of the same left-to-right flow, so "구현 → 리뷰 → PR" is one picture. A run without `--pr` simply has no PR lane.
- **Each ticket node opens a detail modal**, so put the per-ticket specifics there rather than cramming the node: `acceptance` (the ticket's own criteria), `steps` (what happened inside — 티켓 읽기 → `$implement` → 게이트 재검증 → 머지백, each with status), `gateList` (every gate with its `CHECK:` command and expected-vs-actual for the unmet ones), `files`, and `commits`. This is the run's answer to "이 티켓 안에서 무슨 일이 일어났나", and it is the difference between a status light and a report.
- The terminal board stays exactly as it is; this mirrors it, never replaces it. When `$interview-report` reports a `tab` or `path` route instead of a link, say so once, at the first board update, and where the page is. "No link" never becomes "no report".

## Final report (before → after)

The run ends by regenerating the decision graph **with `$interview-report`'s `outcome` block filled in and `progress.state` set to `done`** (that is what stops the page polling), publishing it through `$interview-report` (same link or tab as the rest of the run), and handing the user what it returns — the URL, or the tab plus the path. This happens once, at the true end of the run: after step 9's implement loop and its gate re-verification, after the small path's `$implement`, or — in ship mode — after step 10 leaves the PR merge-ready. Never earlier: a results panel written before the work is verified is a guess.

- **Measure, never estimate.** `git diff --numstat <baseline>..HEAD` for the line counts and `git diff --name-status <baseline>..HEAD` for added / modified / deleted / renamed, against the baseline recorded in step 1. In ship mode measure the PR branch's tip. Every number in the panel and in your terminal summary comes from that output.
- **Classify each file** as `code` / `docs` / `other` (see interview-report's `outcome` spec) and write one Korean line per file saying what it now does — that line is the report, the path alone is not. Leave the run's own bookkeeping (`docs/agents/matt-auto-log/**`, `.unlazy/**`) out of the tally.
- **Then report in the terminal**, short: the artifact link first, the headline counts (생성 / 수정 파일 수, 코드 `+`/`−`, 문서 `+`/`−`), tickets completed, verification results, and the Run id when workers ran. Point at the graph for the decisions themselves — never restate them as prose.

## Interview gate (never skipped)

Autonomous mode removes the *routine* confirms, not the user's last look at the design before code gets written. Right after step 4's report is generated, the pipeline stops — autonomous and `--confirm` alike — and does not open step 5, 6, or 7 until the user answers. It does not require `--orca`; delivery is `$interview-report`'s job.

- **Deliver where the user reads, not a file path.** `$interview-report` publishes the graph and answers with how it was delivered: a public Orca artifact URL, or — when publishing is refused or the profile is signed out — the worktree's Orca browser tab plus the path. Present exactly that, a one-line summary of what the interview settled, and what happens next on approval; when it reports a refusal, relay its one-line reason (it names the setting only a human can flip). The gate holds either way; an unopenable report is not a reason to run ahead, and a missing link is not a reason to skip the live board or the final report.
- **Wait.** No spec, no tickets, no `$implement` while the gate is open. Step 4's board row reads `⛔ interview gate` until it clears, and the wait itself is not an escalation — don't re-ask it as a question the delegate could answer.
- **Say how to answer.** With the link, tell the user their two routes: reply here in the terminal, or edit/flag nodes in the page and hit **수정 내보내기** — and that on the hosted link the page keeps edits only for that page load, so they export before reloading (in the Orca tab edits persist).
- **Clearing it.** A clear go-ahead ("진행", "ok", "go") → continue to step 5. Anything else is a change request, in whichever form it arrives: a terminal reply, a `<slug>.edits.json` saved into `docs/agents/matt-auto-log/`, or that JSON pasted into the chat. Feed it to the delegate, rework the affected interview decisions, record the rework in the decision log, regenerate the report (`$interview-report` keeps the same link or tab), delete a consumed edits file, and present the gate again. Repeat until approved.
- This is the only gate autonomous mode keeps. Steps 5 and 8 stay skipped, and escalation stays exactly as it was.

## Decision-graph report

The user-facing report of what got decided is never prose: it is the `$interview-report` decision-graph HTML at `docs/agents/matt-auto-log/<slug>.html` — an interactive graph showing each pipeline stage in order and, hanging off each stage, the decisions and policies that applied there as editable nodes, with escalations highlighted.

- **Generate** it right after the interview (step 4) — that generation is what the interview gate presents, as an Orca artifact link — and **regenerate** it over the full decision log before the final report (step 9's end, the small path's `$implement`, and after step 10 in ship mode), so the finished graph covers every stage: interview, seam check, ticket breakdown, implement-loop decisions, escalations, ship.
- **Round-trip.** In the graph the user can edit a decision, flag a node as a problem with a comment, and export `<slug>.edits.json`, which they save into `docs/agents/matt-auto-log/`. Whenever matt-auto is invoked (step 1's check) — or the user says mid-run that they edited the graph — read that file: every edited or flagged node is a change request, not a suggestion. Feed it to the delegate, rework from the earliest affected stage (step 8's rework rule), record the rework in the decision log, regenerate the report, then delete the consumed edits file so a stale edit is never applied twice.
- **The final regeneration carries the `outcome` block** — the shipped-changes panel (수정/생성 파일, 코드 및 문서 라인 수) measured from git against step 1's baseline. See Final report.
- The final report still summarizes outcomes in the terminal, but points at the graph for the decisions — never duplicate the full decision list as prose.

## Ship mode (`--dev` / `--main` / `--pr <base>`)

`--dev` targets `dev`, `--main` targets `main`, and `--pr <base>` targets any other base branch. Without one of these, matt-auto never opens a PR — implementation ends with commits on the working branch, exactly as before. `--confirm` and `--free` combine freely with ship mode.

- **PR branch.** Implementation must not land on the base itself. At the start of implementation (step 5 small path, or step 9), if the current branch *is* the base, create `matt-auto/<slug>` from it and check it out; if the user is already on a feature branch, keep it. The branch name is part of the ship plan shown at confirm (recommended: `matt-auto/<slug>`), and in autonomous mode (the default) the recommended name is taken and written to the decision log. All `$implement` subagents commit to this branch.
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
- **Routing.** Opening the PR is mechanical → `matt-fast`. The babysit coordinator → `matt-default` with `ROUTED_EXECUTION=1; use $pr-babysit and shepherd this PR to merge-ready` (it routes its own children: fast for status, default for normal CI fixes, deep for hard failures). Conflict resolution → `matt-deep` (`matt-free` in free-only mode; if unavailable, stop and report rather than fall back to a paid route). On Codex, use the table's direct model/effort overrides for each of these routes. Without automatic routing, use the platform's normal subagent at the effort selected in step 2, and run conflict resolution at `high` or above.
- **Report.** Add to the final report: PR URL, base, PR condition and how it was verified, the ship ledger tally (`met/total`, or `—` without unlazy), babysit cycles run, commits pushed during babysit (including any conflict-resolution merge commits), final check state, and whether it is merge-ready. In autonomous mode the same goes into the decision log.

## Parallel execution (automatic)

No flag turns this on. Step 2 probes Orca; if orchestration answers, step 7 plans the ticket DAG into **waves** and step 9 runs each wave accordingly. It changes only *where implementation workers run*: steps 1–4 and 6–8 are untouched, the decision delegate stays an in-session subagent, and every gate keeps its current meaning. `--parallel N` (default 2, max 4) and `--on <env>` override concurrency and placement; `--orca` is accepted and changes nothing. `--confirm`, `--free`, and ship mode all combine freely.

**Planning the waves (step 7).** You decide this, not the user, and the plan is `$interview-report`'s `plan` block — every wave carries the reason it is shaped that way:

- Start from `$to-tickets`' blocking edges: tickets whose blockers are all satisfied form a candidate wave. That is necessary but not sufficient.
- Keep a candidate **sequential** when the tickets touch the same files or the same section of one file, when one's design is likely to change the other's assumptions, when a ticket is exploratory enough that its outcome reshapes what follows, or when merging them back would collide. Independence in the DAG is not independence on disk — check the paths each ticket will actually touch.
- Cap a parallel wave at the plan's concurrency (default 2, max 4), and prefer fewer, wider waves over many thin ones.
- Give every ticket an `estimateMin` — your own honest guess at its size, which the page renders as 예상 and uses for the percentage and ETA. Never inflate one to make a bar move.
- With Orca unreachable, every wave is `sequential` and the plan says why in `note`. The plan is still published — a sequential plan is a plan.

- **What it is.** Orca orchestration (Run → Task → Dispatch) is the dispatcher for a parallel wave in step 9 — and only that. **Workers buy concurrency and isolation; anything that runs alone runs in-session.** The small path, a sequential wave's tickets, a parallel wave that turned out to hold one ticket, and step 10's babysit all stay in-session routed subagents: a worker there is pure overhead (worktree create + setup, dispatch, `check --wait` polling, merge-back — measured at ten-plus minutes on a one-file change) with nothing gained. Time is cost. The ticket DAG that `$to-tickets` already declared through blocking edges is registered as an Orca Task DAG, and tickets on the frontier run concurrently, each in its own worktree, optionally on another connected Orca server. matt-auto is a *supervised* coordinator — it waits for `worker_done` and verifies — so use the `orchestration` skill's supervised path (`run-create → task-create → worker-start → check --wait`), never `orca-cli`'s full handoff, and never a non-Orca subagent tool for the workers (that would leave no Orca provenance; `task-list --json` / `dispatch-show` is what proves a worker was orchestrated).
- **Preconditions** (probed in step 2, always): `orca status --json` shows a running runtime and `orca orchestration run-list --json` answers (orchestration enabled in Settings › Experimental). On Linux the binary is `orca-ide`; if the `orca` shim fails with `bad option: --no-sandbox` (unprivileged user namespaces disabled), use `orca-ide` from `PATH` for every command and say so once on the board. Every new shell must bind the Run before task commands: `orca orchestration run-use --id <run> --json` (otherwise `run_required`). If `--on <env>` names an environment Orca does not list, escalate — sending the code to another machine is the user's decision, not the delegate's.
- **Routing → worker flags.** Classify each ticket with Model routing exactly as before, then translate the tier into `worker-start` options per the Orca table in `$model-routing` (Codex, Claude, and OpenCode flags, the `--retry-of` rule for Max, and the fallbacks when the runtime rejects a pair). In `--free` mode use only `matt-free*` routes and never start a Claude or Codex worker.
- **The loop (step 9).**
  1. `orca orchestration run-create --objective "<spec title>" --json` once, then `task-create --spec "<worker prompt for ticket>" --deps '[<task ids of its blockers>]' --json` for every ticket. The worker prompt is the same as the in-session one — "read ticket <ref>, then use $implement to build it" — plus the Orca lifecycle lines in `orca-worker-prompt.md` next to this file (report open decisions with `orca orchestration ask`, finish with `worker_done --outcome`). Print the Run id on the board.
  2. For each ready ticket (`task-list --ready --brief --json`), up to `--parallel N`: create the worktree first (`orca worktree create --name matt-auto/<ticket> --json`, parented on the working/PR branch; remote: `new-top-level` with an explicit `--repo` selector after pushing the working branch so the worker starts from the same commit), write the ticket's unlazy ledger into that worktree at `.unlazy/matt-auto/<ticket>.GATES.md` (give every gate `CWD: ../..` — an explicit ledger resolves CHECK relative to the ledger's own directory — and wrap regex expectations in `/…/`, otherwise EXPECT is a plain substring), approve it there (`gate-check.mjs --approve <worktree>/.unlazy/matt-auto/<ticket>.GATES.md` — approvals bind the ledger's absolute path and CWD, so each worktree needs its own), pre-trust the worktree for Claude Code (add the path to `~/.claude.json` `projects` with `hasTrustDialogAccepted: true`; otherwise readiness fails with `codex-trust-workspace` on the folder-trust prompt), and only then `worker-start --task <id> --worktree path:<that worktree> <route flags> --json`. An existing worktree gets a fresh agent terminal without rerunning setup. Remote workers have no local approval; they inspect the ledger and approve it themselves, which is fine because the evidence that counts is produced locally (step 4).
  3. Wait with `check --wait --types worker_done,escalation,question --timeout-ms 900000 --json` — never sleep/poll. A timeout or `{count:0}` is a checkpoint, not a failure; heartbeats and visible activity mean alive, not done. Process the whole Delivery, then `check --ack <delivery_id> --wait …`. A `question` goes to the decision delegate and its answer back via `reply --id <msg_id>`; `ESCALATE` and `escalation` messages go to the real user as in Escalation.
  4. On `worker_done`, verify — the report is a signal, not evidence. Run `gate-check.mjs --reverify` on the ledger inside the worker's worktree (remote worker: it pushed its branch before reporting; fetch it and reverify in a local temporary worktree — execution may be remote, evidence is always produced on the coordinator's machine). Unmet gates go back to the same worker with `send --to dispatch:<id> --subject "unmet: <ids>"` (max 2 retries, then escalate as a handoff); set the task back to `dispatched` with `task-update` so the DAG does not advance on Orca's automatic completion. On `ALL MET`, merge the worktree branch into the working/PR branch (`git merge --no-ff`; a conflict is resolved right there by dispatching `$resolving-merge-conflicts` to `matt-deep` in-session), copy the ledger into the main checkout's `.unlazy/matt-auto/`, and run `--approve --reverify` on it there (the copied ledger already carries evidence, so a plain `--approve` skips its met gates and writes no approval) — `.unlazy/` is ignored by git so the ledger does not travel with the merge, and parallel work must still pass after integration. Also `--reverify` every previously completed ticket's ledger on the merged code, so a later merge cannot silently break an earlier ticket. Only that second `ALL MET` makes the ticket done and unblocks its dependents. Then `worker-release --dispatch <id> --json`.
  5. `worker-start` may return `failed` at stage `dispatch_input` with `agent_prompt_stalled` even though the prompt was delivered: Orca gives the TUI five seconds to report a working state and Claude Code often takes longer. Read the terminal (`orca terminal read --terminal <handle>`); if the TASK block is there and the agent is working, do **not** retry (that duplicates the ticket). The dispatch is dead but the worker is not: keep waiting on `check --wait` — its report arrives as `Rejected worker_done: …` in the Run mailbox — verify exactly as in step 4, then `task-update --id <task> --status completed` yourself since automatic completion needs a live dispatch, and close the terminal with `worker-stop`/`terminal close` (`worker-release` returns `release_unknown` for a failed dispatch). Note the stall on the board.
  6. Recovery is conditional: `worker-show --dispatch <id>` `ready` → keep waiting; `failed`/`stopped` → `worker-start --task <task> --retry-of <id>` with an explicit `--worktree` and agent choice; `outcome_unknown` → `worker-stop`, inspect, then retry. Never stop or abandon a worker because of a timeout, idle TUI, heartbeat, or question. If the session is lost, rebind with `run-list` → `run-use --id <run>` and rebuild the frontier from `task-list`.
- **Ship (step 10).** Everything in step 10 stays in-session: open the PR, run `$pr-babysit` as a Default-route in-session subagent (`ROUTED_EXECUTION=1; use $pr-babysit on PR <n> and shepherd it to merge-ready`), and verify the ship ledger. Its report is input; the ship ledger's own `--reverify` is completion, as in Ship mode. Release the Run's workers before this step begins.
- **unlazy boundaries.** As `$loop-gates` says: one Solo ledger per ticket; Orca owns dispatch, waiting, and retry, unlazy owns gates and evidence; never unlazy's Parallel/Orchestrated mode alongside Orca, never the Stop hook in worker worktrees.
- **Report and log.** Add the Run id, per-ticket dispatch ids and worktrees, remote placements, and merge order to the final report; in autonomous mode the same goes into the decision log. Release every worker before reporting unless the user asked to keep one alive.

## Fallback

- Platform without subagents: run the flow human-in-the-loop instead — every sub-skill question goes to the user directly, and step 8's confirm is simply to-tickets' own approval. Autonomous mode is impossible here — there is no delegate to run unattended, so behave as if `--confirm` was passed.
- Delegate lost mid-pipeline: respawn it with the Q&A log so far as context.
- weed-harness shared skills missing (`$loop-report`, `$model-routing`, `$loop-gates`): say so once on the board, then — no report page (the decision log is the only record; the gate presents it as a path), platform-default subagent for every role, no gates. Do not reimplement any of the three inline.

## Red flags — you are drifting off the flow

- Answering a sub-skill's question yourself instead of routing it to the delegate → the delegate's independent judgment is the point; you grading your own recommendations is not.
- Publishing tickets before step 8's confirm in `--confirm` mode → that confirm is the gate the user explicitly asked back for; don't take it away.
- Letting the artifact go stale while the terminal board moves on, or marking a ticket `blocked` without the checkable reason → the link is the user's window into a run they are not watching.
- Dropping the live board or the final before → after report because the artifact link was refused → `$interview-report` has a route for every case; the link is only one of them. A run whose HTML still shows the interview gate after the tickets ran is exactly this failure.
- Running `orca artifacts`, `tab create`, or `reload --page` from here → delivery has one owner; say publish and relay what comes back.
- Reporting file or line counts that were not measured from `git diff --numstat` against step 1's baseline → the results panel's whole value is that its numbers are checkable.
- Starting the spec, tickets, or `$implement` while the interview gate is unanswered → that gate is the one thing autonomous mode does not skip, and a published link the user hasn't replied to is not approval.
- Treating autonomous mode as license to skip escalation too → it removes the effort question and the confirms, nothing else. A material decision still stops the pipeline and goes to the real user.
- Running autonomously without a decision log file, or letting it fall behind → it's the only place mid-pipeline decisions are visible when nothing is presented live.
- Reporting decisions as prose instead of the decision-graph HTML, or finishing a run while an unconsumed `<slug>.edits.json` sits in `docs/agents/matt-auto-log/` → the graph is the report, and a graph edit is a change request, not a suggestion.
- Asking the user mid-pipeline about non-material decisions → that is the delegate's job now; the user opted out of those questions.
- Scoring ambiguity percentages or inventing readiness gates → no Matt skill does this. Drop it. (Step 9's per-ticket unlazy ledger is the one sanctioned exception, and it verifies implementation, never design readiness.)
- Marking a ticket complete while its unlazy ledger has unmet gates, or trusting the subagent's "done" instead of running `--reverify` → the ledger exists precisely because a confident done report is not evidence.
- Writing specs or notes outside the tracker, `CONTEXT.md`/ADRs, the decision log, or `$interview-report`'s output → wrong artifact system.
- Running several implementation workers in parallel outside a wave the plan declared parallel, or beyond the blocking edges to-tickets declared → Matt's loop is one ticket per fresh context; a parallel wave only executes the DAG that already exists.
- Creating a parallel wave's workers with a non-Orca subagent tool and calling it orchestrated → no Orca provenance; only workers visible in `task-list` / `dispatch-show` count.
- Stopping or abandoning an Orca worker because of a timeout, idle TUI, or heartbeat → those mean alive, not failed.
- Starting an Orca worker for work that runs alone — the small path, a sequential wave's ticket, a one-ticket wave, babysit → workers are for concurrency; alone, they only add minutes and tokens.
- Merging a worker's branch on its `worker_done` alone, or marking a ticket done before the ledger passes again on the merged code → the worker's report is a signal; the coordinator's local `--reverify` after merge is the evidence.
- Letting the progress board go stale, inventing a per-platform format for it, or writing it to a file → one uniform markdown table, reprinted at every transition, display only.
- Opening a PR without `--dev` / `--main` / `--pr <base>`, or opening it before the PR condition is measured as met → the user, not the agent, decides when a PR exists.
- Merging the PR, force-pushing the PR branch, or rebasing it to clear a conflict → merge-ready is the goal; merge the base in, resolve, push normally.
- Calling the PR merge-ready from local checks, your own reading of the checks page, or pr-babysit's "merge-ready" report while the ship ledger is not `ALL MET` → the ledger's `--reverify` against GitHub state is the evidence.
- Opening the PR while a PR-condition gate is unmet or was "met" by the delegate's say-so → PR conditions are measured, and manual ones are answered by the user.
