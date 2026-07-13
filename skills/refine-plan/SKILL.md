---
name: refine-plan
description: Iteratively harden a feature plan via Codex↔Claude consensus loop until it passes Architect + Critic verdict. Mirrors OMC ralplan with 5-round minimum, 10-round cap, Codex as default Architect/Critic. Use after /to-prd to lock plan.md before /goal-set.
argument-hint: "<feature-id> [--deliberate] [--architect claude] [--critic claude]"
---

# /refine-plan — Phase 4 of the team pipeline

Iteratively refine `.team/tasks/<feature-id>/plan.md` until consensus PASS, mirroring OMC's ralplan workflow.

## Inputs

- `.team/tasks/<feature-id>/prd.md` — PRD (from `/to-prd`)
- `.team/tasks/<feature-id>/plan.md` — initial plan draft

## Outputs

- `plan.md` — locked, RALPLAN-DR formatted, ADR appended on APPROVE
- `.refine-history.md` — per-round Architect/Critic feedback + diff summary
- `.refine-verdict.json` — `{rounds, final, stuck, deliberate}`

## Roles

| Role | Default | Override flag | Responsibility |
|---|---|---|---|
| **Planner** | Claude (this session) | (always Claude) | Edits `plan.md` in-place per feedback |
| **Architect** | Codex | `--architect claude` | Steelman antithesis + tradeoff + principle-violation flags |
| **Critic** | Codex | `--critic claude` | Quality criteria + testability + verdict |

> **Steps 2 (Architect) and 3 (Critic) MUST run sequentially.** Always await Architect output before invoking Critic. Do NOT parallelize.

## Constants

```
MIN_ROUNDS = 5
MAX_ROUNDS = 10
DELIBERATE_KEYWORDS = ["auth", "security", "migration", "destructive",
                      "production", "compliance", "PII", "public API",
                      "breaking change"]
```

## Mode Selection

Auto-enable `--deliberate` mode if `prd.md` or `plan.md` contains any keyword from `DELIBERATE_KEYWORDS` (case-insensitive). User can force with `--deliberate`.

In deliberate mode the plan is REQUIRED to include:
- Pre-mortem with ≥3 failure scenarios (each: blast radius + mitigation)
- Test plan covering unit + integration + e2e + observability

## Loop

```
TASK_DIR=".team/tasks/<feature-id>"
HISTORY="$TASK_DIR/.refine-history.md"
VERDICT="$TASK_DIR/.refine-verdict.json"

for round in 1..MAX_ROUNDS:
  (1) Planner edits plan.md
  (2) Architect critique  (await complete)
  (3) Critic verdict      (after Architect)
  (4) Apply verdict logic
  (5) Append round trace to .refine-history.md

terminate per termination rules below
```

### Step 1 — Planner (Claude, in-place)

Edit `plan.md` to RALPLAN-DR format with these sections:
- Principles (3-5)
- Decision Drivers (top 3)
- Viable Options (≥2 with pros/cons; if only one viable, document why others were invalidated)
- Chosen Option + rationale tied to Drivers
- Architecture
- Implementation Steps
- Test Plan (unit/integration/e2e; +observability in deliberate mode)
- Pre-mortem (3 scenarios in deliberate mode)

Round 1 = initial pass. Subsequent rounds apply the previous round's Architect + Critic feedback.

### Step 2 — Architect (Codex by default)

Invoke via the `codex:rescue` agent or `codex --print`. Prompt:

```
You are the Architect reviewing a feature plan.

Read:
- $TASK_DIR/prd.md
- $TASK_DIR/plan.md

Provide your review in JSON:
{
  "antithesis": "<strongest steelman antithesis to the chosen option>",
  "tradeoffs": ["<concrete tradeoff tension 1>", "..."],
  "synthesis": "<how the antithesis insight could be incorporated, or null>",
  "principle_violations": ["<violations of stated Principles, if any>"],
  "deliberate_check": "PASS|FAIL|N/A",
  "summary": "<one-paragraph verdict>"
}

If deliberate mode is active (check plan.md for Pre-mortem section), set deliberate_check to PASS only if Pre-mortem has ≥3 realistic scenarios with mitigations AND Test Plan has all 4 categories. Otherwise FAIL with explanation in summary.

Output ONLY the JSON, no preamble or trailing prose.
```

**MUST await Architect completion before Step 3.**

### Step 3 — Critic (Codex by default, AFTER Architect)

Invoke with the Architect JSON in context:

```
You are the Critic. Given:
- $TASK_DIR/prd.md
- $TASK_DIR/plan.md
- Architect review (JSON below)

Evaluate the plan against:
1. Principle-option consistency (chosen option actually serves Principles)
2. Fair alternatives (Options are genuine, not strawmen)
3. Risk mitigation clarity
4. Testable acceptance criteria
5. Concrete verification steps
6. Deliberate mode (if active): pre-mortem + expanded test plan are substantive

Architect output:
$ARCHITECT_JSON

Output JSON:
{
  "verdict": "APPROVE|ITERATE|REJECT",
  "issues": [
    {"severity": "high|med|low", "where": "<section>", "fix": "<actionable change>"}
  ],
  "missing": ["<gap>", "..."],
  "summary": "<one-paragraph verdict>"
}

Verdict guide:
- APPROVE: plan is execution-ready
- ITERATE: small-scope fixes needed
- REJECT: needs structural rework

Output ONLY the JSON.
```

### Step 4 — Verdict handling

```
if verdict == REJECT or verdict == ITERATE:
  collect (architect.principle_violations + critic.issues + critic.missing)
  → next round (Planner applies feedback in Step 1)

if verdict == APPROVE:
  if round < MIN_ROUNDS:
    log "early APPROVE at round=N, continuing to MIN_ROUNDS"
    → next round (Planner refines further, even without specific feedback,
      e.g. tighten Principles, sharpen Test Plan, add edge cases)
  if round >= MIN_ROUNDS:
    break with success
```

### Step 5 — Append to .refine-history.md

For each round, append:

```markdown
## Round N (YYYY-MM-DD HH:MM)
**Architect:** <summary>
**Critic verdict:** APPROVE|ITERATE|REJECT
**Critic issues:** <bulleted>
**Plan diff:** <what Planner changed in this round>
```

## STUCK escalation

If at any point:
- Codex returns malformed JSON 3 times consecutively in the same step, OR
- A Codex tool call fails 3 times consecutively

Then:
1. Append `[STUCK round=N step=<step> reason="<reason>"]` to `.refine-history.md`
2. Write `.refine-verdict.json` with `{"stuck": true, ...}`
3. Halt — wait for human intervention. Do **NOT** auto-retry beyond 3 attempts. Do **NOT** silently fall back to Claude (the user can pass `--architect claude` / `--critic claude` to manually switch).

Per project rule: failure → wait for human.

## Termination

### Success path

When `round >= MIN_ROUNDS AND last_verdict == APPROVE`:

1. Append final ADR section to `plan.md`:
   ```markdown
   ## ADR (locked at round <N>)
   - **Decision:** <chosen option>
   - **Drivers:** <top 3 from Principles + drivers>
   - **Alternatives considered:** <other options + why invalidated>
   - **Why chosen:** <rationale>
   - **Consequences:** <expected positive + negative>
   - **Follow-ups:** <deferred work>
   ```
2. Write `.refine-verdict.json`:
   ```json
   {"rounds": <N>, "final": "APPROVE", "stuck": false, "deliberate": <bool>}
   ```
3. Report summary to user: rounds taken, deliberate mode on/off, recommend `/goal-set <feature-id>`.

### Failure path (MAX_ROUNDS exhausted)

When `round == MAX_ROUNDS AND last_verdict != APPROVE`:

1. Output the current plan.md to user as the "best effort" version
2. Write `.refine-verdict.json`:
   ```json
   {"rounds": 10, "final": "FAIL", "stuck": false, "deliberate": <bool>}
   ```
3. Halt — surface to user. Do **NOT** proceed to `/goal-set` automatically.

## Phase boundaries

`/refine-plan` ONLY refines plan.md. It does NOT:
- Write goal.md (that's `/goal-set`)
- Dispatch implementation (that's `/team-dispatch`)
- Modify code in the worktree
- Run any mutating shell commands beyond editing the three plan-related files

After APPROVE, recommend the user run `/goal-set <feature-id>` next.

## Differences vs OMC ralplan

| Aspect | OMC ralplan | /refine-plan |
|---|---|---|
| Starting point | Creates plan from scratch | Refines existing `plan.md` |
| Default Architect/Critic | Claude | **Codex** (cross-check) |
| Min rounds | not specified | **5 enforced** |
| Pre-execution gate | Yes (vague-prompt detection) | No (PRD acts as gate) |
| Post-APPROVE action | Dispatches to team/ralph/autopilot | Stops — awaits `/goal-set` |
| Interactive mode | `--interactive` flag | Always non-interactive (full auto, halt on STUCK) |

## Related skills

- `/to-prd` — produces the PRD this skill consumes
- `ouroboros:ralph` — pure self-referential loop, no consensus structure
- `/goal-set` — the next phase after this skill returns APPROVE
