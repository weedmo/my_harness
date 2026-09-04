---
name: autocode
description: "Hypothesis-driven parallel code improvement loop. A strategist on the expensive model tier proposes falsifiable hypotheses with pre-committed if_confirmed / if_refuted actions; experimenters routed by hypothesis difficulty implement them concurrently in git worktrees; the coordinator measures serially, keeps by arithmetic, and feeds every single result back to the strategist so the frontier is revised as results arrive, not per batch. Subcommands: init [N], run [--parallel N] [--on <env>], status, resume."
argument-hint: "<subcommand: init|run|status|resume> [max experiments] [--parallel N] [--on <env>]"
---

# Autocode — Hypothesis-Driven Parallel Improvement

Autonomous loop that improves one measurable metric of a codebase as fast as possible per
wall-clock hour. Three ideas make it fast:

1. **Hypotheses, not experiments.** The strategist emits falsifiable claims, each carrying the
   experiment that tests it, the files it touches, a difficulty tier, and what to do next in
   either outcome. Replanning after a result is a delta to the frontier, never a fresh plan.
2. **Parallel where it is safe, serial where it is not.** Hypotheses with disjoint `touches`
   run concurrently, each in its own git worktree. Measurement is a serial critical section
   because concurrent benchmarks contaminate each other.
3. **Route by difficulty.** The strategist runs on the expensive tier (it decides what is worth
   trying); each experimenter runs on the cheapest tier its hypothesis needs. Keep/discard,
   scheduling, and merging are arithmetic — no model at all.

Inspired by [autoresearch](https://github.com/karpathy/autoresearch). The run is visible the
whole time on a live **experiment board** — one HTML page built and delivered by the shared
`$loop-report` skill (weed-harness) and republished on every state change (see 3I) — and
termination is backed by runnable [unlazy](https://github.com/Leonxlnx/unlazy) gates through
the shared `$loop-gates` convention instead of self-assessment (see 2E). If those shared
skills are missing, say `weed-harness 3.x required: <skill> missing` once and continue with
the fallback each of them names.

## Subcommands

| Command | Action | User Confirmation |
|---|---|---|
| `/autocode init [N]` | Interview → `program.md`. N = max experiments (default 20, 0 = unlimited) | Required (interview + approval) |
| `/autocode run [--parallel N] [--on <env>]` | Run the loop until budget, target, or exhaustion | None (autonomous) |
| `/autocode status` | Frontier, running experiments, best metric, routing tally | None |
| `/autocode resume` | Continue from `state.json` after interruption | None |

## Step 0: Paths

```
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
AUTOCODE_DIR="$PROJECT_ROOT/.autocode"
PROGRAM_FILE="$AUTOCODE_DIR/program.md"
RESULTS_FILE="$AUTOCODE_DIR/results.tsv"
STATE_FILE="$AUTOCODE_DIR/state.json"
HYP_DIR="$AUTOCODE_DIR/hypotheses"
WORKTREE_DIR="$AUTOCODE_DIR/worktrees"
LESSONS_DIR="$AUTOCODE_DIR/lessons"
LOGS_DIR="$AUTOCODE_DIR/logs"
RETRO_DIR="$AUTOCODE_DIR/retrospectives"
REPORT_DIR="$AUTOCODE_DIR/report"          # autocode.data.json / autocode.html / autocode.delivery.json
```

## Step 1: Parse Subcommand

- No args or `init` → Step 2. Optional integer N = `max_experiments`.
- `run` → Step 3. `--parallel N` (default from program.md, max 4) and `--on <env>` (Orca
  environment for remote workers) override program.md for this run only.
- `status` → Step 4. `resume` → Step 5.

---

## Step 2: Init (`/autocode init [N]`)

### 2A: Reconnaissance (no questions yet)

Scan the repo before asking anything: language and build system, test command, existing
benchmark or profiling scripts, hot-path candidates (large functions, loops over collections,
I/O in request paths), and how many modules the target spans. Use these facts to propose
defaults in the interview and to classify problem difficulty in 2C.

### 2B: Interview (one question at a time, dynamic follow-ups)

Ask with `AskUserQuestion`, one question at a time, proposing the reconnaissance-derived
answer as the recommended option. Loop until every required field is filled.

| Field | Question | Default |
|---|---|---|
| `target_files` | "Which file(s) or directories may experiments modify?" | — |
| `metric_name` | "What metric measures success? (e.g. p95_latency_ms, bundle_bytes)" | — |
| `metric_command` | "Shell command that prints the metric as a single number on the last line?" | — |
| `metric_direction` | "Lower or higher is better?" | lower |
| `guard_command` | "Tests/lint/typecheck that must pass before a change is measured?" | detected test cmd |
| `worktree_setup` | "Command to prepare a fresh checkout so guard and metric run? (deps, build)" | none |
| `scope` | "How far may changes go? function / module / system" | module |
| `forbidden_zones` | "Files or areas that must not change?" | none |
| `max_experiments` | "Maximum number of experiments? (0 = unlimited)" | N or 20 |
| `performance_target` | "Target metric value for early termination?" | none |
| `parallel` | "How many experiments may run concurrently? (1–4)" | 2 |

Follow-ups: a directory target → "Any hot-path files inside it?"; scope ≥ module → "Must public
interfaces stay compatible?"; system scope → "External systems or data formats involved?";
guard is tests only → "Add typecheck or lint to the guard?"; metric command runs > 60 s →
"Is there a shorter proxy metric for screening?" (store as `screen_command`, optional).

### 2C: Difficulty classification (strategist tier)

Classify the problem from the recon and the answers, and show the classification in the
approval step so the user can override it:

- **standard** → strategist runs on the Deep route (`strategist`, opus/high).
- **hard** → strategist runs on the Max route (`strategist-max`, fable/xhigh) from the start.

Classify **hard** when any of: scope is system-wide; the target spans more than three modules;
the metric is already within a known bound (the user or recon says prior optimization attempts
plateaued); concurrency, distributed state, or numerical stability is involved; or the user
says it is hard. Otherwise **standard**. The tier can still escalate at run time (3G).

### 2D: Generate `program.md`

~~~markdown
# Autocode Program

## Target
- **files**: {target_files}
- **read_only_context**: {reference-only files}

## Metric
- **name**: {metric_name}
- **command**: `{metric_command}`
- **direction**: {lower|higher}
- **screen_command**: `{screen_command|null}`

## Guard
```
{guard_command}
```

## Worktree
- **setup**: `{worktree_setup|null}`

## Constraints
- **scope**: {function|module|system}
- **interface_compat**: {true|false}
- **forbidden_zones**: [{forbidden_zones}]
- **immutable_constraints**: [{from follow-ups}]

## Budget
- **max_experiments**: {N} (0 = unlimited)
- **performance_target**: {value|null}
- **parallel**: {1-4}

## Routing
- **problem_difficulty**: {standard|hard}
- **strategist_tier**: {deep|max}
- **experimenter_routes**: fast | default | deep (per hypothesis, chosen by the strategist)

## Plateau
- **consecutive_discard_threshold**: 5
- **window**: 8
- **unlazy_gates**: {true|false}

## Strategy Hints
{user hints or extra context}
~~~

Also create `results.tsv` with header
`seq\thypothesis\troute\tcommit\tmetric\tdelta\tstatus\tnote`, the directories from Step 0,
and add `.autocode/` to `.gitignore` (ask first; worktrees live under it and must never be
committed).

### 2E: Runnable completion gates (unlazy, optional)

Follow `$loop-gates` (shared): locate unlazy once; if missing, ask once whether to install it
(`npx skills add Leonxlnx/unlazy -g`), on decline set `unlazy_gates: false` and continue. If
present, write `$AUTOCODE_DIR/GATES.md` with one gate per script under `$AUTOCODE_DIR/verify/`
(portable Node, no dependencies):

- `verify-guard.mjs` — runs the guard on the experiment branch; prints `autocode gate passed: guard` on exit 0.
- `verify-metric.mjs` — re-runs the metric on the experiment branch and asserts it is at least as good as `best_metric` in `state.json` within the noise band; prints `autocode gate passed: metric`. It re-measures the claim; it never trusts the recorded number.
- `verify-target.mjs` — only with `performance_target`; re-measures and asserts the target is met; prints `autocode gate passed: target`.

Scripts read thresholds from `program.md` / `state.json`, so `CHECK:` lines never change during
a run and one approval keeps the loop autonomous. Show the user `GATES.md` and every script,
then with explicit consent approve the ledger once (`gate-check.mjs --approve`). The
coordinator re-verifies it at termination (3F); the retry bound, the handoff on unmet gates,
and the boundaries with Orca are loop-gates'. Do not install unlazy's Stop hook.

### 2F: Approval

Present `program.md` (including the difficulty classification and strategist tier) via
`AskUserQuestion`: **[Approve and save] [Edit and regenerate] [Start over]**.

---

## Step 3: Run (`/autocode run`)

The session running this skill is the **coordinator**. It owns scheduling, measurement,
keep/discard, merging, state, and the conversation with the strategist. It never edits target
code itself and never reasons about what to try next — that is the strategist's job.

### 3A: Pre-flight

1. `program.md` exists, target files exist, working tree clean (else stop and say so).
2. Create the experiment branch `autocode/{YYYY-MM-DD-HHMM}` from the current branch. `best`
   always means the head of this branch.
3. Run the guard on the unmodified code; abort if it fails.
4. Resolve routing (3H). Probe Orca only if `--on <env>` was given or program.md `parallel` > 1
   and the user asked for Orca at init: `orca status --json`, `orca orchestration run-list
   --json` (if the `orca` shim fails with `bad option: --no-sandbox`, retry with `orca-ide`).
   Without Orca, workers are in-session subagents in local worktrees — that is the default
   and is not a degraded mode.
5. Load lessons from `$LESSONS_DIR/*.json`.
6. **Probe report delivery** — have `$loop-report` **probe** (see 3I) and print the answer with
   the other pre-flight facts (`Report delivery: link` / `tab — <why>` / `path — <why>`), so
   the user knows before the first experiment where the board will be. Use `orca-ide` when
   the `orca` shim fails with `--no-sandbox`, as in step 4.

### 3B: Baseline and noise band

Run the metric command **three times** on the unmodified code, serially. Validate each value is
a finite number (abort with the raw output otherwise). Record:

- `baseline` = median of the three.
- `noise_band` = max |run − median|, floored at 0.5% of |median|.

A change counts as an improvement only when it beats `best_metric` by more than `noise_band` in
the configured direction. This is the only keep/discard rule in the whole loop.

Write `state.json`:

```json
{
  "branch": "autocode/2026-09-03-1410",
  "baseline": 182.4,
  "noise_band": 2.1,
  "best_metric": 182.4,
  "best_commit": "a1b2c3d",
  "experiments_done": 0,
  "max_experiments": 20,
  "parallel": 2,
  "strategist_tier": "deep",
  "strategist_agent_id": null,
  "running": [],
  "consecutive_discards": 0,
  "escalated": false,
  "terminated_reason": null
}
```

Display the baseline, noise band, branch, parallelism, strategist tier, and worker placement,
then **publish the board for the first time** (3I) — `progress.state: running`, the metric
strip with baseline and noise band, an empty frontier. From here on every state change
republishes it.

### 3C: Spawn the strategist (persistent)

Spawn one strategist for the whole run on the tier from `program.md` (`auto-loop:strategist`
or `auto-loop:strategist-max` on Claude Code; see 3H for other platforms). Keep its agent id in
`state.json` and continue the same conversation with `SendMessage` for every result — do not
respawn per event; its accumulated context is what makes replanning cheap.

Its first prompt carries the strategist brief (below), `program.md`, the baseline and noise
band, the lessons, and the paths of the target files, and asks for the **initial frontier**:
at least `2 × parallel` hypotheses, preferring disjoint `touches`.

**Strategist brief** (include verbatim):

> You are the strategist of an autocode run. You only produce hypotheses; you never edit code
> and never run the metric. Each hypothesis is a JSON object written to
> `.autocode/hypotheses/H{NNN}.json` with the schema in your prompt. Prefer hypotheses that are
> independent (disjoint `touches`) so they can run concurrently. Assign `difficulty` honestly:
> `fast` for one-site mechanical changes, `default` for multi-site changes within a module,
> `deep` for algorithm replacement, cross-module restructuring, or anything touching invariants.
> Pre-commit `if_confirmed` and `if_refuted`: the concrete next hypotheses or cancellations each
> outcome implies. When the coordinator sends you a result, reply with a frontier delta
> (`add`, `cancel`, `reprioritize`, `escalate`, `note`) — not a new plan. Respect
> `forbidden_zones`, `scope`, and `immutable_constraints`. If the current framing is spent, set
> `escalate: true` and say why instead of producing variations of refuted ideas.

**Hypothesis schema** (`.autocode/hypotheses/H007.json`):

```json
{
  "id": "H007",
  "claim": "Per-request JSON schema compilation dominates p95; caching the compiled validator removes it.",
  "experiment": "Memoize compileSchema() by schema identity in src/validate.ts; public API unchanged.",
  "expected_delta": "-15% to -25% p95_latency_ms",
  "touches": ["src/validate.ts"],
  "depends_on": [],
  "difficulty": "fast",
  "if_confirmed": ["Apply the same memoization to the response serializer (src/serialize.ts)", "Add an LRU bound once hit ratio is known"],
  "if_refuted": ["Schema compile is off the hot path; profile the handler (new hypothesis) before more caching"],
  "priority": 2,
  "status": "pending"
}
```

`status` moves `pending → running → measured → keep | discard | crash | conflict | interaction | cancelled`.

**Strategist reply schema** (on every result event):

```json
{
  "add": [ { "...hypothesis..." } ],
  "cancel": ["H003"],
  "reprioritize": { "H005": 1 },
  "escalate": false,
  "note": "H007 confirmed at -19%; H003 assumed compile was cheap, cancelled."
}
```

### 3D: Scheduler loop (event-driven)

The coordinator runs this loop until 3F terminates it. Every state change is written to
`state.json` immediately (atomic write), every result is appended to `results.tsv`, and every
state change also **republishes the board** (3I): a dispatch, a measurement, a keep/discard,
a strategist delta applied, a plateau or escalation. Not on a timer, not per commit.

```
loop:
  # 1. FILL — keep `parallel` experiments running
  frontier = hypotheses with status=pending whose depends_on are all keep, sorted by priority
  for H in frontier while len(running) < parallel:
      skip H if H.touches intersects touches of any running hypothesis
      dispatch(H)                              # 3D-1
  # 2. WAIT for the first completion (never for the whole batch)
  H = next finished experimenter (task notification)
  # 3. MEASURE — serial critical section (3D-2)
  # 4. DECIDE + MERGE — arithmetic (3D-3)
  # 5. FEED BACK — one message to the strategist, apply its delta (3D-4)
  # 6. TERMINATE? (3F) else loop
```

If the frontier is empty while nothing is running, ask the strategist for a refill once; if it
returns nothing twice in a row, terminate with `exhausted`.

#### 3D-1: Dispatch one hypothesis

1. Worktree: `git worktree add "$WORKTREE_DIR/H{id}" -b "autocode/H{id}" "$best_commit"`. Run
   `worktree_setup` inside it if set (note the duration on the first run; if it dominates, say so
   in the final summary).
2. Route by `difficulty` (3H) and spawn the experimenter **in the background** with this prompt:

> Implement exactly hypothesis `{id}` in the worktree `{path}` (branch `autocode/H{id}`).
> Hypothesis: {claim}. Experiment: {experiment}. Expected: {expected_delta}. You may edit only
> {touches}; never touch {forbidden_zones}; respect {immutable_constraints}. Steps: (1) read the
> relevant code, (2) make the smallest change that tests the hypothesis, (3) run the guard
> `{guard_command}` — on failure fix and retry at most twice, (4) `git add -A && git commit -m
> "experiment(H{id}): {short}"`, (5) write `.autocode/hypotheses/H{id}.result.json` in the main
> checkout with `{ "status": "implemented" | "crash" | "beyond_scope", "commit": "<sha>",
> "summary": "<what changed>", "observations": "<anything the strategist should know>",
> "obstacle": "<only for crash/beyond_scope>" }`. Do **not** run the metric command; the
> coordinator measures. Do not merge, do not touch other worktrees, do not install hooks.

   Orca placement (only when `--on <env>` was given or the user chose Orca at init and 3A's probe
   succeeded): `orca orchestration run-create` once per run, then `task-create` +
   `worker-start --task <id> --worktree path:<worktree> <route flags>` with the same prompt plus
   Orca lifecycle lines (report with `worker_done`, ask with `orchestration ask`). Route flags
   come from `$model-routing`'s Orca table for the tier (3H). Verify a `worker_done` by reading
   the result file and the branch; it is a signal, not evidence.

3. Set `H.status = running`, add to `state.running`, log the route in `results.tsv` later.

#### 3D-2: Measure (serial)

The coordinator itself runs the metric, one experiment at a time, in the worktree:

1. If `result.status` is `crash` → record `crash`, skip measurement.
2. If `beyond_scope` → re-dispatch once on the next route up (fast→default→deep); a `deep`
   `beyond_scope` becomes `discard` with note `beyond_scope`. Do not count it as an experiment.
3. Otherwise run `metric_command` in the worktree, redirect output to
   `$LOGS_DIR/H{id}.log`, parse the last line as a number. Non-finite → `crash`. If
   `screen_command` exists, run it first and skip the full metric when the screen is worse than
   `best` by more than `noise_band` (record `discard`, note `screened`).
4. Nothing else may run the metric while this step runs. Experimenters never run it.

#### 3D-3: Decide and merge (arithmetic)

```
improved = better_by(metric, best_metric) > noise_band   # in metric_direction
if not improved:
    status = discard; consecutive_discards += 1
else:
    git merge --no-ff autocode/H{id}  into the experiment branch
    if conflict:  git merge --abort; status = conflict   # another keep touched the same lines
    else:
        re-measure once on the merged branch (serial, same rules)
        if better_by(merged, best_metric) > noise_band:
            status = keep; best_metric = merged; best_commit = HEAD; consecutive_discards = 0
        else:
            git reset --hard HEAD~1; status = interaction   # kept changes cancelled each other
```

Then: append `results.tsv` (`seq, H{id}, route, commit, metric, delta, status, note`), write a
lesson to `$LESSONS_DIR/lesson_{seq}.json` (`{iteration, type, description, action, tags}`),
`git worktree remove --force "$WORKTREE_DIR/H{id}"`, `git branch -D autocode/H{id}`,
`experiments_done += 1`.

`conflict` and `interaction` are informative: they mean two hypotheses were not independent.
Both go to the strategist as such.

#### 3D-4: Feed back one result

Send the strategist a single message:

> Result for H{id}: status={status}, metric={metric} (best {best_metric}, noise ±{noise_band}),
> delta={delta}. Experimenter summary: {summary}. Observations: {observations}. Consecutive
> discards: {n}. Frontier now: {ids and statuses}. Execute the pre-committed
> `if_confirmed` / `if_refuted` of H{id} as concrete hypotheses or cancellations, then reply
> with a frontier delta.

Apply the delta: write new hypothesis files, mark cancelled ones (a cancelled hypothesis that is
already running is left to finish — its worktree is cheap, and its result is still evidence),
update priorities. Go back to FILL immediately; do not wait for other running experiments.

### 3E: Plateau and escalation

Plateau when `consecutive_discards ≥ 5` **or** no `keep` in the last 8 measured results.

1. Ask the strategist for a retrospective → `$RETRO_DIR/retro_{n}.md` (metric trend, effective
   patterns, refuted directions, remaining opportunities).
2. If `strategist_tier` is `deep` and not yet `escalated`: spawn `strategist-max` with the
   retrospective, `program.md`, `results.tsv`, and the lessons; replace `strategist_agent_id`;
   set `escalated = true`; request a fresh frontier. This is the only automatic path to the Max
   tier, and it happens once per run.
3. If already on `max` (or the strategist itself replied `escalate: true` while on `max`):
   ask it for one final frontier; if that also yields no keep, terminate with `plateau`.

### 3F: Termination

Stop the loop when the first of these holds, after letting running experiments finish and be
measured (they are paid for; their evidence is still useful):

- `experiments_done ≥ max_experiments` (when > 0) → `budget_exhausted`
- `best_metric` meets `performance_target` → `target_reached`
- frontier empty and the strategist returned nothing twice → `exhausted`
- plateau persisted through 3E → `plateau`

Then: remove leftover worktrees, release any Orca dispatches, leave the experiment branch checked
out at `best_commit`.

When `unlazy_gates: true`, run `node "$UNLAZY_DIR/scripts/gate-check.mjs" --reverify
$AUTOCODE_DIR/GATES.md` first, per `$loop-gates`. Compose the summary only on `ALL MET`;
otherwise record `ABANDON: <id> <reason>` in the ledger and end as an explicit handoff naming
the unmet gates. `target_reached` in particular must be backed by the target gate's measured
evidence.

Then **publish the board one last time** (3I) with `progress.state: "done"`,
`run.terminatedReason` set, and the `outcome` block: `outcome.files` measured with
`git diff --numstat <branch base>..<best_commit>` / `--name-status`, one Korean line per file,
`.autocode/**` left out. That final page is the report the user keeps; the terminal summary
below points at it.

**Final summary**:

```
## Autocode Final Summary

- Branch: autocode/{stamp} @ {best_commit}
- Baseline: {baseline} → Best: {best_metric} ({improvement}%), noise band ±{noise_band}
- Experiments: {done} ({kept} keep, {discarded} discard, {crashed} crash, {conflict} conflict, {interaction} interaction)
- Wall clock: {elapsed}; {experiments/hour}; measurement time share {pct}%
- Strategist: {deep|max}{, escalated at experiment N}
- Experimenter routes: fast {n} / default {n} / deep {n}; re-routed {n}
- Termination: {reason}

### Kept changes (in merge order)
1. H{id} — {claim} ({delta}%)
...

### Refuted hypotheses worth remembering
- H{id} — {claim} → {what the result showed}
```

### 3G: Failure handling

- An experimenter that produces no result file within the time budget (default 30 min, or
  `worktree_setup` + guard duration × 3 once known) is stopped and recorded as `crash` with note
  `timeout`.
- A worktree that cannot be created (dirty state, name clash) is removed and re-created once;
  then the hypothesis is `discard`ed with note `worktree`.
- If the metric command fails on the experiment branch after a merge, the merge is reverted and
  the run pauses with a clear message — a broken measurement is not something to loop past.

### 3H: Model routing

The tiers, the exact model/effort pair per platform, the `spawn_agent` / Claude agent / Orca
`worker-start` dispatch mechanics, and the escalation ladder live in the shared
**`$model-routing`** skill (weed-harness). Read it; do not restate pairs here. autocode's
roles map onto its tiers:

| autocode role | Tier | Claude Code agent | Use when |
|---|---|---|---|
| Strategist | Deep | `auto-loop:strategist` | Default strategist tier |
| Strategist (escalated) | Max | `auto-loop:strategist-max` | `problem_difficulty: hard`, or escalation in 3E — the only role that uses Max |
| Experimenter fast | Fast | `auto-loop:experimenter-fast` | One-site mechanical change: constant/flag tuning, obvious API swap, dropping redundant work |
| Experimenter default | Default | `auto-loop:experimenter-default` | Multi-site change inside a module, new helper, data-structure swap, loop restructuring |
| Experimenter deep | Deep | `auto-loop:experimenter-deep` | Algorithm replacement, cross-module restructuring, concurrency, invariants |

- The strategist assigns `difficulty`; the coordinator only translates it into a route. When an
  experimenter reports `beyond_scope`, re-dispatch once on the next route up (3D-2) and mark
  the hypothesis `rerouted`. **Deep is the ceiling for experimenters**; Max is reserved for the
  strategist.
- Orca workers take the tier's `worker-start` flags from `$model-routing`'s Orca table.
- On a platform with neither named agents nor model overrides, use the platform's normal
  subagent for every role, name the intended tier in the prompt, and say so once at start.

### 3I: The experiment board

The board is the run's status page and, at the end, its report — built and delivered by
`$loop-report` with autocode's own view (`assets/view.html` next to this file, its data checks
in `assets/validate.py`). autocode owns the data; loop-report owns the page around it and the
route (artifact link, Orca browser tab, or path — see its SKILL.md). Never run `orca artifacts`
/ `tab` / `reload` from here; say probe or publish and relay the answer.

**Publish** = write `$REPORT_DIR/autocode.data.json`, then hand it to `$loop-report`:

```
python3 <loop-report's dir>/assets/render.py \
  --data .autocode/report/autocode.data.json \
  --out  .autocode/report/autocode.html \
  --view <this skill's dir>/assets/view.html
```

and let loop-report push it on the run's route (it keeps `autocode.delivery.json` beside the
page so every republish lands on the same link or tab). Publish first after the baseline (3B),
then on every state change (3D), on plateau/escalation (3E), and last at termination (3F) with
`progress.state: "done"` and the `outcome`.

**Data** — the common keys follow loop-report's contract (`title`, `slug: "autocode"`,
`generated`, `summary`, `progress { state, updated (from the clock), startedAt, current, note,
blockers }`, `outcome`); the view's keys are:

```json
"run": {
  "branch": "autocode/2026-09-04-1410", "bestCommit": "a1b2c3d",
  "metric": { "name": "p95_latency_ms", "direction": "lower", "baseline": 182.4, "noiseBand": 2.1, "best": 151.0, "target": 120 },
  "budget": { "done": 6, "max": 20, "parallel": 2, "placement": "local" },
  "strategist": { "tier": "deep", "escalated": false, "consecutiveDiscards": 1 },
  "terminatedReason": null
},
"hypotheses": [
  { "id": "H007", "seq": 5, "claim": "…", "experiment": "…", "expectedDelta": "-15% ~ -25%",
    "status": "keep", "difficulty": "fast", "route": "experimenter-fast",
    "worker": { "model": "haiku", "effort": "low", "worktree": ".autocode/worktrees/H007", "dispatchId": "" },
    "touches": ["src/validate.ts"], "dependsOn": [], "priority": 2,
    "metric": 151.0, "delta": -19.2, "commit": "9f8e7d6", "startedAt": "…", "measuredAt": "…",
    "ifConfirmed": ["…"], "ifRefuted": ["…"], "note": "…", "obstacle": "", "rerouted": false }
]
```

- `hypotheses` mirrors `hypotheses/*.json` + `results.tsv`: every hypothesis the run has seen,
  with `status` as in 3C (`pending … cancelled`), `seq` = measurement order (measured ones
  only), `metric` the measured value, `delta` the signed percent against the best at the time,
  `worker` the model/effort the route resolved to (plus worktree, and the dispatch id for an
  Orca worker). Claims, notes, and obstacles are translated into one plain Korean line each;
  the strategist's English JSON is not pasted through.
- `run.terminatedReason` is null until 3F, then one of `budget_exhausted`, `target_reached`,
  `exhausted`, `plateau`, or `paused` (3G's measurement pause). `validate.py` refuses an
  `outcome` without it.
- `progress.current` is the one line the coordinator is on right now ("H007 측정 중", "전략가
  프론티어 갱신 대기"); `progress.blockers` carries anything that stops the run — 3G's paused
  measurement, a worktree that cannot be created — with the checkable fact in `detail`.
- The page derives everything else (improvement %, the trend chart, routes tally, ETA from the
  median experiment duration); never pre-sum numbers into the data.

---

## Step 4: Status (`/autocode status`)

Read `state.json`, `results.tsv`, and `hypotheses/*.json`; display:

```
## Autocode Status

**Branch**: autocode/{stamp} @ {best_commit}
**Best**: {metric_name} {best_metric} (baseline {baseline}, {improvement}%, noise ±{noise_band})
**Experiments**: {done}/{max} — {kept} keep · {discarded} discard · {crashed} crash · {conflict} conflict · {interaction} interaction
**Running** ({n}/{parallel}): H012 (default, 4 min) · H015 (fast, 1 min)
**Frontier**: {pending count} pending — next: H016 (p1), H013 (p2)
**Strategist**: {deep|max}{ (escalated)} · consecutive discards {n}
**Routes used**: fast {n} / default {n} / deep {n}
**Rate**: {experiments/hour}, measurement share {pct}%
**Board**: {link | tab + path | path} (from autocode.delivery.json)
```

## Step 5: Resume (`/autocode resume`)

1. Require `program.md` and `state.json`; otherwise say `No run to resume. Run /autocode init
   then /autocode run.`
2. Check out the experiment branch. For every id in `state.running`: if its worktree and result
   file exist, measure it (3D-2/3D-3); if the worktree exists without a result, remove it and set
   the hypothesis back to `pending`.
3. Respawn the strategist on the recorded tier with `program.md`, `results.tsv`, the lessons,
   the latest retrospective if any, and the current frontier — it has no memory of the previous
   session, so this prompt is its whole context.
4. Continue at 3D.

---

## File structure

```
.autocode/                          # gitignored
├── program.md                      # init output
├── state.json                      # coordinator state, rewritten on every event
├── results.tsv                     # append-only experiment log
├── hypotheses/
│   ├── H001.json                   # strategist output
│   └── H001.result.json            # experimenter output
├── worktrees/H001/                 # one git worktree per running experiment (removed after measure)
├── lessons/lesson_001.json
├── logs/H001.log                   # metric stdout/stderr
├── retrospectives/retro_1.md       # written on plateau
├── GATES.md                        # [unlazy] runnable termination gates
├── verify/*.mjs                    # [unlazy] gate scripts
└── report/                         # the experiment board (see 3I)
    ├── autocode.data.json          # what autocode writes
    ├── autocode.html               # what loop-report renders
    └── autocode.delivery.json      # the route loop-report keeps (link / tab / path)
```

## Anti-patterns

- Coordinator editing target code or proposing hypotheses itself → roles exist so the expensive
  reasoning is spent once, on hypotheses, and the cheap tiers do the typing.
- Experimenter running the metric → measurement is serial by design; a parallel benchmark is
  noise dressed as data.
- Waiting for a whole batch before replanning → the frontier is revised per result; idle slots
  are wasted wall clock.
- Respawning the strategist per result → its accumulated context is what makes a delta reply
  cheap. Respawn only on escalation or resume.
- Keeping a change inside the noise band → the only keep rule is `better_by > noise_band`.
- Trusting a `worker_done` or an experimenter's "it's faster" → status comes from the
  coordinator's own measurement, nothing else.
- Running one hypothesis at a time when `parallel > 1` and the frontier has disjoint `touches` →
  that is the sequential loop this design replaces.
- Letting the board go stale while `state.json` moves on, or skipping a publish because the
  artifact link was refused → the page is the user's window into a run they are not watching;
  loop-report has a route for every case, and the timing is the coordinator's.
- Running `orca artifacts` / `tab` / `reload` from here, or splicing the page by hand →
  delivery and the build have one owner; say publish and relay what comes back.
