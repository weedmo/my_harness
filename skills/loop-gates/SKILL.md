---
name: loop-gates
description: "The shared completion-discipline layer for every delegated loop in this harness — how matt-auto, pr-babysit, merging-pr-queue, and autocode use the unlazy skill (Leonxlnx/unlazy) so that \"done\" is a measured verdict, not a confident report: locating unlazy, offering to install it, deriving a runnable GATES.md ledger per unit of work, approving only commands the coordinator wrote, re-verifying with gate-check.mjs after every delegate returns, the retry bound, and the boundaries with Orca orchestration. Reference skill: read it when a loop starts its verification; do not invoke it standalone."
---

# Loop gates (shared, on top of unlazy)

A loop that runs for hours on the user's behalf has one structural weakness: every unit of work returns as a *report* from a delegate, and a confident "done" is not evidence. unlazy turns completion into a ledger of runnable checks the coordinator re-executes itself. This skill is the harness's convention for using it — the same in every loop, so a ticket, a PR, and an experiment all end the same way.

unlazy itself is not vendored here: it is an upstream skill installed with `npx skills add Leonxlnx/unlazy -g` (which links it into `~/.agents/skills/unlazy` and the per-CLI skill dirs). weed-harness's installer and its `auto-update.sh` hook keep it present; this file only says how the loops use it.

## Locate it, once per run

```bash
UNLAZY_DIR=""
for d in "$HOME/.claude/skills/unlazy" "$HOME/.codex/skills/unlazy" "$HOME/.agents/skills/unlazy"; do
  [ -f "$d/scripts/gate-check.mjs" ] && UNLAZY_DIR="$d" && break
done
```

Present → gates are on for the run; put the tally on the loop's board. Missing → ask once whether to install it (`npx skills add Leonxlnx/unlazy -g`); on decline, or on a platform where you cannot ask, say `unlazy absent — verification is the delegate's own checks` once and continue. Gates never block a run from starting; they change what counts as finished.

## The ledger

One ledger per unit of work — a matt-auto ticket, a PR, an autocode run — at `.unlazy/<loop>/<unit>.GATES.md`, written **before** the work is dispatched, derived from the unit's own acceptance criteria:

- One gate per independently required outcome. Runnable (`CHECK:` + `EXPECT:`, typically the repo's own test/build/lint commands, `gh` for PR state, a metric script for a measurement) wherever a command can decide it; manual only when no command can, and then its evidence is the user's explicit answer — never the delegate's.
- `CHECK:` is code. The coordinator writes these commands and therefore approves the ledger itself (`node "$UNLAZY_DIR/scripts/gate-check.mjs" --approve <ledger>`); never approve a ledger you did not write or read. Give every gate `CWD: <repo root relative to the ledger>` when the ledger lives outside the repo root (an explicit ledger resolves CHECK relative to its own directory), and wrap regex expectations in `/…/` — otherwise EXPECT is a plain substring.
- Keep `CHECK:` lines stable for the run: read thresholds from files (`state.json`, `program.md`) rather than baking numbers into the command, so one approval keeps the loop autonomous.
- Tell the delegate the ledger path defines "done" for its unit. Keep `.unlazy/` in the project's ignore rules.

## Verify, retry, escalate

- When the delegate returns, the **coordinator** runs `gate-check.mjs --reverify <ledger>` itself. The delegate's own claim, a worker's `worker_done`, a "tests pass" in a report — all signals, none evidence.
- Unmet gates go back to the same delegate route with the unmet ids, **at most twice**; then the unit stops as an explicit handoff to the user naming the unmet gates. A stop that is not completion becomes `ABANDON: <id> <reason>` in the ledger — never a quiet success and never a silently skipped unit.
- A unit is complete only on `ALL MET`. Work that integrates (a merged branch, a merged PR) is re-verified **after** integration on the merged code, and every previously completed unit's ledger is re-run then too, so a later merge cannot silently break an earlier one.
- Report the tally (`met/total`) on the loop's board and in the loop's report data (`gates: { met, total }`, and `gateList` with `CHECK`, expected-vs-actual for the unmet ones) — an unmet gate the user cannot see is an unmet gate they cannot act on.

## Boundaries

- Gates verify *execution*, never design readiness: interviews, specs, plans, and hypotheses gain no gates. Do not invent readiness scores.
- Gates never replace escalation. A material decision still stops the loop and goes to the user; a gate that "passes" by the delegate's say-so is not a pass.
- When Orca orchestration dispatches the work, Orca owns dispatch, waiting, and retry; unlazy owns gates and evidence. Do **not** use unlazy's Parallel/Orchestrated mode (`OWNS:` leases, dispatch waves, `dispatch.json`) alongside Orca — worktree isolation replaces ownership leases, and overlapping edits surface as merge conflicts. One Solo ledger per unit.
- A worker in its own worktree gets its own copy of the ledger and its own approval there (approvals bind the ledger's absolute path and CWD). The evidence that counts is still produced on the coordinator's machine: fetch the branch, re-verify locally.
- Do not install unlazy's Stop hook from a loop, and never in worker worktrees; the loop's retry bound is the stop policy.

## Red flags

- Marking a unit complete while its ledger has unmet gates, or trusting the delegate's "done" instead of running `--reverify` → the ledger exists precisely because a confident report is not evidence.
- Approving a ledger the coordinator did not write, or one inherited from a worker without reading its `CHECK:` lines → `CHECK:` is code that runs on the user's machine.
- A `CHECK:` that bakes in a number the run will change → the approval breaks mid-run and the loop stops being autonomous.
- Retrying past two rounds, or restarting the unit on a higher tier to "get it green" → that is the handoff moment; report the unmet gates.
- Using unlazy's dispatch/lease machinery under Orca → two dispatchers; the ledger loses its meaning.
- Gates on the design stages, or readiness percentages → verification is for work that ran, not for decisions.
