# Autocode v2 — PGE Extension Design Spec

**Date**: 2026-04-16
**Status**: Draft
**Author**: weed + Claude

## Overview

Extend the existing `/autocode` skill with a PGE (Plan-Generate-Execute) team-based strategic loop for software performance optimization. The key addition is an **outer loop** that performs retrospective analysis, external research, and architecture redesign when experiments plateau — enabling the system to escape local optima autonomously.

## Goals

1. **Structured HITL interview** — brainstorming-pattern init that dynamically generates follow-up questions until all required fields are filled
2. **PGE team loop** — Claude team agents (Planner/Generator/Evaluator + on-demand Researcher/Architect) running experiments with retrospective-driven architecture redesign
3. **Hook-based persistence** — new persistent-mode hook loop via `.omc/state/autocode-pge-state.json`, independent of ralph/autopilot

## Non-Goals

- ML/AI model training optimization (use `/auto_research` instead)
- Replacing existing single-agent mode (preserved as `mode=single`)
- Human approval gates for architecture redesign (fully autonomous)

---

## Architecture

### Dual-Mode Execution

```
/autocode init → extended HITL interview → program.md
  → "Single or PGE?" → mode saved to program.md

/autocode run
  ├── mode=single → existing experiment loop (unchanged)
  └── mode=pge   → PGE strategic loop (new)
```

### PGE Loop Structure

```
┌─────────────── Outer Loop (strategy) ───────────────┐
│                                                      │
│  Architect → architectures/v{N}.md                   │
│       ↓                                              │
│  Planner → experiment plan based on v{N}             │
│       ↓                                              │
│  ┌──── Inner Loop (experiments) ────┐                │
│  │ Generator: code edit → guard → measure            │
│  │ Evaluator: keep/discard + plateau check           │
│  │     plateau? NO → next experiment                 │
│  │              YES → exit inner loop                │
│  └──────────────────────────────────┘                │
│       ↓                                              │
│  Evaluator: retrospective (metrics + code patterns)  │
│  Researcher: external research (spawn)               │
│  Architect: redesign decision (spawn)                │
│       ↓                                              │
│  Termination check:                                  │
│    budget exhausted → terminate                      │
│    target reached → early terminate                  │
│    else → outer loop continues                       │
└──────────────────────────────────────────────────────┘
```

---

## State Machine

### State File: `.omc/state/autocode-pge-state.json`

```json
{
  "active": true,
  "mode": "pge",
  "session_id": "<session_id>",
  "outer_loop": {
    "architecture_version": 1,
    "redesign_count": 0
  },
  "inner_loop": {
    "iteration": 5,
    "max_iterations": 50,
    "phase": "experiment",
    "consecutive_discards": 0,
    "improvement_rate_window": []
  },
  "plateau": {
    "detected": false,
    "trigger_reason": null,
    "researcher_pending": false,
    "architect_pending": false
  },
  "termination": {
    "reason": null,
    "target_metric": null,
    "target_reached": false,
    "budget_exhausted": false
  },
  "best": {
    "metric": 145.3,
    "commit": "a1b2c3d",
    "architecture_version": 1
  }
}
```

### Phase Transitions

```
[pge_init] → [plan] → [experiment] → [evaluate]
                ↑                         │
                │                    plateau?
                │                   /       \
                │                 NO        YES
                │                  ↓          ↓
                │            [experiment]  [retrospect]
                │                              ↓
                │                        [research]
                │                              ↓
                │                        [redesign]
                │                              ↓
                │                     budget check
                │                    /            \
                │                 OK            exhausted
                │                  ↓                ↓
                └──────────── [plan]          [terminated]

[evaluate] → target reached? → YES → [terminated]
```

### Plateau Detection (Compound Trigger)

```
plateau_detected = (
  consecutive_discards >= 3
  AND improvement_rate(last_5) < 0.5%
) OR (
  consecutive_discards >= 5
) OR (
  time_since_last_keep > time_budget * 3
)
```

### Hook Integration

- Extends `persistent-mode.mjs` — `autocode-pge-state.json` with `active=true` activates boulder pattern
- Loop continues until phase reaches `terminated`
- Atomic writes on every phase transition
- Session-scoped ownership prevents cross-session interference

---

## HITL Interview Design

### Pattern

Brainstorming-style: one question at a time, dynamic follow-up questions based on answers, loop until all required fields are filled.

### Required Fields Schema

```
autocode_target_files          "Which files should the agent modify?"
autocode_metric_name           "What metric measures success?"
autocode_metric_command        "Shell command to extract the metric?"
autocode_metric_direction      "lower or higher is better?"
autocode_guard_command         "Tests/lint that must pass before accepting a change?"
autocode_architecture_context  "Describe the current system structure"
autocode_scope_boundary        "How far can changes go? (function/module/system)"
autocode_forbidden_zones       "Any areas that must not be touched?"
autocode_max_iterations        "Maximum experiment count?" (default: 10, 0=unlimited)
autocode_performance_target    "Target metric value?" (optional, early termination)
```

### Dynamic Follow-Up Rules

| Answer | Follow-up |
|--------|-----------|
| target is a directory | "Any hot-path files in this directory?" |
| guard is tests only | "Include type check or lint in the guard?" |
| scope >= module | "Must interface compatibility be maintained?" |
| scope = system-wide | "Any external system dependencies?" |
| architecture has constraints | "What are the immutable constraints?" |

### Defaults (Not Asked)

| Field | Default |
|-------|---------|
| `autocode_time_budget` | unlimited |
| `autocode_redesign_budget` | unlimited |

### Completion Flow

1. Check all required fields are filled
2. If any empty → generate question for that field
3. Generate `program.md`
4. Present to user for approval: `[Approve] [Edit] [Start over]`
5. Ask execution mode: `[Single] [PGE]`
6. Save mode to `program.md`

---

## PGE Agent Roles

### Core Agents (active every iteration)

| Agent | Model | Role | Input | Output |
|-------|-------|------|-------|--------|
| **Planner** | sonnet | Create experiment plan from architecture + prior results | `architectures/v{N}.md`, `results.tsv`, `lessons/` | `plans/plan_{iter}.md` |
| **Generator** | sonnet | Edit code → run guard → measure metric | plan, target files | commit, metric value, status |
| **Evaluator** | opus | Analyze results, plateau detection, keep/discard | `results.tsv`, recent experiments, code diffs | plateau verdict, retrospective |

### On-Demand Agents (plateau only)

| Agent | Model | Role | Input | Output |
|-------|-------|------|-------|--------|
| **Researcher** | sonnet | Web/codebase search for new optimization techniques | retrospective, current architecture, exhausted directions | `research/research_{N}.md` |
| **Architect** | opus | Redesign architecture based on research + experiment history | research, `results.tsv`, `architectures/v{N}.md` | `architectures/v{N+1}.md` |

### Communication

All file-based via `.autocode/` directory. No inter-agent messaging.

---

## PGE Execution Flow

### Inner Loop (Experiments)

```
for each iteration in 1..max_iterations:
  1. Planner: write plans/plan_{iter}.md
  2. Generator:
     a. Read plan, edit target files
     b. git commit -m "experiment: {description}"
     c. Run guard → fail: retry x2, still fail → crash, revert
     d. Run metric command
  3. Evaluator:
     a. Judge result (keep/discard/crash)
        - keep: update best baseline
        - discard: git reset --hard HEAD~1
        - crash: git reset --hard HEAD~1
     b. Append to results.tsv
     c. Extract lesson → lessons/lesson_{N}.json
     d. Plateau compound check
        - not plateau → next iteration
        - plateau → exit inner loop
```

### Outer Loop (Strategic — on plateau)

```
on plateau_detected:
  1. Evaluator: write retrospectives/retro_v{N}.md
     - Metric trend analysis
     - Effective vs ineffective change patterns
     - Exhausted direction list

  2. Researcher: spawn (foreground, need results)
     - Input: retrospective + current architecture + exhausted directions
     - Web search: optimization techniques, benchmarks, papers
     - Codebase search: similar patterns, unexplored areas
     → research/research_{N}.md

  3. Architect: spawn (foreground, need results)
     - Input: retrospective + research + full experiment history + current architecture
     - Decision: is architecture change promising?
       YES → write architectures/v{N+1}.md
       NO  → keep current architecture, update strategy hints only
     → update architecture_version in state

  4. Termination check:
     iteration >= max_iterations → terminated (budget exhausted)
     performance_target reached  → terminated (target met)
     else → Planner receives new architecture, inner loop resumes
```

### Single Mode

Existing autocode Step 3 unchanged. No outer loop. Plateau triggers legacy PIVOT/REFINE/PROCEED logic.

---

## File Structure

```
.autocode/
├── program.md                    # init output (unified schema)
├── results.tsv                   # full experiment log
├── mode.txt                      # single | pge
├── checkpoint.json               # resume state
├── lessons/
│   ├── lesson_001.json           # self-learning entries
│   └── lesson_002.json
├── logs/                         # experiment stdout/stderr
├── plans/
│   ├── plan_001.md               # per-iteration experiment plans
│   └── plan_002.md
├── architectures/
│   ├── v1.md                     # initial architecture
│   ├── v2.md                     # 1st redesign
│   └── v3.md
├── retrospectives/
│   ├── retro_v1.md               # v1 architecture retrospective
│   └── retro_v2.md
└── research/
    ├── research_001.md           # Researcher outputs
    └── research_002.md

.omc/state/
└── autocode-pge-state.json       # loop orchestration state
```

---

## program.md Unified Schema

```markdown
# Autocode Program

## Target

- **files**: {autocode_target_files}
- **read_only_context**: {reference-only files}

## Metric

- **name**: {autocode_metric_name}
- **command**: `{autocode_metric_command}`
- **direction**: {lower|higher}

## Guard

```
{autocode_guard_command}
```

## Architecture

- **context**: {autocode_architecture_context}
- **scope**: {autocode_scope_boundary}
- **interface_compat**: {true|false}
- **forbidden_zones**: [{autocode_forbidden_zones}]
- **immutable_constraints**: [{constraints from follow-up}]

## Termination

- **max_iterations**: {autocode_max_iterations} (0=unlimited)
- **performance_target**: {autocode_performance_target|null}

## Mode

- **execution_mode**: {single|pge}

## Pipeline

- **selected_stages**: [{stage IDs}]
- **quality_gate_stages**: [5, 9, 20]
- **lessons_enabled**: true
- **researchclaw_available**: {true|false}

## Plateau Detection

- **consecutive_discard_threshold**: 3
- **improvement_rate_threshold**: 0.5
- **hard_discard_limit**: 5

## Strategy Hints

{user-provided hints or dynamically collected additional context}
```

### Field Usage by Mode

| Field | Single | PGE |
|-------|--------|-----|
| Target, Metric, Guard | used | used |
| Architecture section | ignored | required — Planner/Architect reference |
| Termination | max_iterations only | max_iterations + performance_target |
| Plateau Detection | legacy PIVOT/REFINE | outer loop trigger |
| Mode | `single` | `pge` |

---

## Subcommands (Updated)

| Command | Action |
|---------|--------|
| `/autocode install` | Install AutoResearchClaw (unchanged) |
| `/autocode init` | Extended HITL interview → program.md → mode selection |
| `/autocode run` | Execute based on mode (single or pge) |
| `/autocode status` | Show progress including architecture version and redesign history |
| `/autocode resume` | Resume from checkpoint (supports both modes) |

---

## Design Decisions & Rationale

1. **Hybrid A+ team composition** over pure 3-agent or 5-agent — CCG analysis showed 3-agent core wins on token efficiency for inner loop, while on-demand Researcher/Architect provides deep analysis quality at plateau without constant coordination overhead.

2. **Hook-based loop (Option B)** over Claude Team native (Option C) — CCG unanimous: single authoritative state file, stateless agent spawning for context freshness, better debugging, cleaner state separation between orchestration and experiment data.

3. **Brainstorming-pattern HITL** — one question at a time with dynamic follow-ups ensures all required information is gathered without overwhelming the user. Required fields act as completion gate.

4. **Versioned architecture documents** — enables comparison across redesigns, retrospective quality, and rollback if a redesign direction proves worse.

5. **Iteration-only budget** — time budget and redesign count default to unlimited. Single `max_iterations` counter simplifies termination logic: once iterations are exhausted, nothing else runs.

6. **Unified init, split run** — single init flow collects all information (PGE fields included), mode selection at the end. Avoids two separate init paths while keeping run-time behavior cleanly separated.
