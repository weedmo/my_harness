---
name: autocode
description: "Autonomous code improvement loop with PGE (Plan-Generate-Execute) team mode. Single-agent mode: sequential experiments with PIVOT/REFINE logic. PGE mode: team-based experiments with retrospective-driven architecture redesign. Optional 23-stage research pipeline (AutoResearchClaw). Subcommands: install, init, run, status, resume."
argument-hint: "<subcommand: install|init|run|status|resume> [iterations]"
---

# Autocode — Autonomous Code Improvement

Autonomous experiment loop for code improvement with two execution modes:

- **Single mode**: One agent modifies code, measures metrics, keeps improvements, discards regressions.
  PIVOT/REFINE decision logic for strategy adjustment within a fixed architecture.
- **PGE mode**: Team of agents (Planner/Generator/Evaluator) runs experiments. On plateau,
  spawns Researcher and Architect to find new optimization directions and redesign the architecture.
  Escapes local optima through retrospective-driven architecture evolution.

Both modes support bounded iterations, quality gates, self-learning from past failures,
and an optional 23-stage research pipeline via [AutoResearchClaw](https://github.com/aiming-lab/AutoResearchClaw).

Inspired by [autoresearch](https://github.com/karpathy/autoresearch) — same pattern, generalized beyond ML training.

> **For ML-specific research** (model training, hyperparameter tuning, architecture experiments), use `/auto_research` instead. It includes deep-interview initialization, ML domain knowledge, and experiment categorization.

## Subcommands

| Command | Action | User Confirmation |
|---------|--------|-------------------|
| `/autocode install` | Clone AutoResearchClaw + pip install | Not needed |
| `/autocode init [N]` | Extended HITL interview, generate `program.md`, select mode (single/pge). N = max iterations (default 10, 0 = unlimited) | Required |
| `/autocode run` | Execute based on mode in `program.md` (single or pge) | Not needed (autonomous) |
| `/autocode status` | Show progress, including architecture version and redesign history (pge) | Not needed |
| `/autocode resume` | Resume from checkpoint (supports both modes) | Not needed |

## Procedure

### Step 0: Detect Project Root and Researchclaw

```
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
AUTOCODE_DIR="$PROJECT_ROOT/.autocode"
PROGRAM_FILE="$AUTOCODE_DIR/program.md"
RESULTS_FILE="$AUTOCODE_DIR/results.tsv"
LOGS_DIR="$AUTOCODE_DIR/logs"
ANALYSIS_DIR="$AUTOCODE_DIR/analysis"
LESSONS_DIR="$AUTOCODE_DIR/lessons"
CHECKPOINT_FILE="$AUTOCODE_DIR/checkpoint.json"
```

Check researchclaw availability:
```bash
python -c "import researchclaw" 2>/dev/null && echo "available" || echo "unavailable"
```

Store result as `RESEARCHCLAW_AVAILABLE` (true/false) for all subsequent steps.

### Step 1: Parse Subcommand

- `install` -> **Install workflow** (Step 1A)
- No args or `init` -> **Init workflow** (Step 2)
- `run` -> **Run workflow** (Step 3)
- `status` -> **Status workflow** (Step 4)
- `resume` -> **Resume workflow** (Step 5)

Parse iteration count from args: `/autocode init 10` -> `max_iterations=10`. Default: 10. If 0: unlimited (legacy infinite loop).

---

### Step 1A: Install (`/autocode install`)

Install AutoResearchClaw for enhanced pipeline capabilities.

1. Check if already installed:
   ```bash
   python -c "import researchclaw" 2>/dev/null
   ```
   If import succeeds, print version and exit: `researchclaw is already installed.`

2. Clone and install:
   ```bash
   RESEARCHCLAW_DIR="$HOME/.local/share/researchclaw"
   if [ ! -d "$RESEARCHCLAW_DIR" ]; then
     git clone https://github.com/aiming-lab/AutoResearchClaw.git "$RESEARCHCLAW_DIR"
   fi
   cd "$RESEARCHCLAW_DIR" && pip install -e .
   ```

3. Verify:
   ```bash
   python -c "import researchclaw; print(researchclaw.__version__)"
   ```

4. Print result: `AutoResearchClaw installed successfully. Pipeline stages and validators are now available.`

---

### Step 2: Init (`/autocode init [N]`)

Interactive interview to generate a project-specific `program.md`.

#### 2A: Parse Iteration Count

Extract N from arguments. Examples:
- `/autocode init` -> `max_iterations=10`
- `/autocode init 20` -> `max_iterations=20`
- `/autocode init 0` -> `max_iterations=0` (unlimited)

#### 2B: Gather Information (Brainstorming Pattern)

Ask questions **one at a time** using `AskUserQuestion`. Generate dynamic follow-up questions based on answers. Loop until all required fields are filled.

**Required fields** (init cannot complete until all are filled):

| Field | Question | Default |
|-------|----------|---------|
| `autocode_target_files` | "Which file(s) should the agent modify?" | — |
| `autocode_metric_name` | "What metric measures success? (e.g., latency_ms, bundle_bytes)" | — |
| `autocode_metric_command` | "Shell command to extract the metric as a single number?" | — |
| `autocode_metric_direction` | "Is lower or higher better?" | — |
| `autocode_guard_command` | "What must pass before accepting a change? (tests, lint, type check)" | — |
| `autocode_architecture_context` | "Describe the current system structure" | — |
| `autocode_scope_boundary` | "How far can changes go? (function / module / system)" | — |
| `autocode_forbidden_zones` | "Any areas that must not be touched?" | `[]` |
| `autocode_max_iterations` | "Maximum experiment count?" | `10` |
| `autocode_performance_target` | "Target metric value? (optional, for early termination)" | `null` |

**Defaults (not asked):**

| Field | Default |
|-------|---------|
| `autocode_time_budget` | unlimited |
| `autocode_redesign_budget` | unlimited |

**Dynamic follow-up rules:**

After each answer, check if a follow-up question is needed:

| Answer Pattern | Follow-up Question |
|----------------|-------------------|
| `autocode_target_files` is a directory | "Any hot-path files in this directory?" |
| `autocode_guard_command` is tests only | "Include type check or lint in the guard?" |
| `autocode_scope_boundary` >= module | "Must interface compatibility be maintained?" |
| `autocode_scope_boundary` = system-wide | "Any external system dependencies?" |
| `autocode_architecture_context` mentions constraints | "What are the immutable constraints?" |

**Completion gate:**

After each answer, check the required fields table. If any required field (without a default) is still empty, ask the next question for that field. If all required fields are filled, proceed to Stage Selection (2C).

**Interview order** (recommended, but adapt based on answers):
1. `autocode_target_files` (+ follow-up if directory)
2. `autocode_metric_name`
3. `autocode_metric_command`
4. `autocode_metric_direction`
5. `autocode_guard_command` (+ follow-up if tests only)
6. `autocode_architecture_context` (+ follow-up if constraints mentioned)
7. `autocode_scope_boundary` (+ follow-up if module or system)
8. `autocode_forbidden_zones`
9. `autocode_max_iterations`
10. `autocode_performance_target`

#### 2C: Stage Selection UI

After gathering basic info, present the 23-stage pipeline via `AskUserQuestion` with multiSelect.

**Stages grouped by phase:**

| ID | Phase | Stage | Default |
|----|-------|-------|---------|
| 1 | A: Scoping | Topic initialization | ON |
| 2 | A: Scoping | Problem decomposition | ON |
| 3 | B: Literature | Search strategy | ON |
| 4 | B: Literature | Collect sources | ON |
| 5 | B: Literature | Screen sources (GATE) | ON |
| 6 | B: Literature | Extract findings | ON |
| 7 | C: Synthesis | Cluster findings | ON |
| 8 | C: Synthesis | Hypothesis generation | ON |
| 9 | D: Experiment Design | Design experiments (GATE) | ON |
| 10 | D: Experiment Design | Code generation | ON |
| 11 | D: Experiment Design | Resource planning | ON |
| 12 | E: Execution | Run experiments | ON |
| 13 | E: Execution | Iterative refinement | ON |
| 14 | F: Analysis | Result analysis | ON |
| 15 | F: Analysis | PIVOT/REFINE/PROCEED decision | ON |
| 16 | G: Paper Writing | Outline | OFF |
| 17 | G: Paper Writing | Draft | OFF |
| 18 | G: Paper Writing | Peer review | OFF |
| 19 | G: Paper Writing | Revision | OFF |
| 20 | H: Finalization | Quality gate (GATE) | ON |
| 21 | H: Finalization | Archive results | OFF |
| 22 | H: Finalization | Export artifacts | OFF |
| 23 | H: Finalization | Citation verification | OFF |

**Autocode defaults**: Phases A-F + Stage 20 (quality gate). Phases G and H (except 20) are OFF by default. User can toggle any stage on/off.

#### 2D: Generate program.md

Create `$AUTOCODE_DIR/program.md` with the gathered information:

~~~markdown
# Autocode Program

## Target

- **files**: {autocode_target_files}
- **read_only_context**: {any files the agent should read but not modify}

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
- **interface_compat**: {true|false, from follow-up question}
- **forbidden_zones**: [{autocode_forbidden_zones}]
- **immutable_constraints**: [{constraints from follow-up}]

## Termination

- **max_iterations**: {autocode_max_iterations} (0=unlimited)
- **performance_target**: {autocode_performance_target|null}

## Mode

- **execution_mode**: {single|pge, set in Step 2E}

## Pipeline

- **selected_stages**: [{list of stage IDs from 2C}]
- **quality_gate_stages**: [5, 9, 20]
- **lessons_enabled**: true
- **researchclaw_available**: {true|false}

## Plateau Detection

- **consecutive_discard_threshold**: 3
- **improvement_rate_threshold**: 0.5
- **hard_discard_limit**: 5

## Strategy Hints

{Optional: user-provided hints or dynamically collected additional context}
~~~

Also initialize:
- `$AUTOCODE_DIR/results.tsv` with header: `iteration\tstage\tcommit\tmetric\tstatus\tdescription\tdelta`
- `$AUTOCODE_DIR/logs/` directory
- `$AUTOCODE_DIR/analysis/` directory
- `$AUTOCODE_DIR/lessons/` directory
- `$AUTOCODE_DIR/checkpoint.json` with initial state

Add `.autocode/` to `.gitignore` if not already there (ask user first).

Present the generated program.md via `AskUserQuestion` with options:
[Approve and save] [Edit and regenerate] [Start over]

#### 2E: Mode Selection

After the user approves `program.md`, ask via `AskUserQuestion`:

> How should experiments run?
>
> 1. **Single** — One agent, sequential experiments. Classic autocode loop with PIVOT/REFINE logic.
> 2. **PGE** — Team of agents (Planner/Generator/Evaluator). On plateau, spawns Researcher
>    and Architect to find new optimization directions and redesign the architecture.

Store the chosen mode in:
- `$AUTOCODE_DIR/mode.txt` (`single` or `pge`)
- `program.md` → `## Mode` → `execution_mode: {single|pge}`

If PGE mode is selected, also initialize:
- `$AUTOCODE_DIR/plans/` directory
- `$AUTOCODE_DIR/architectures/` directory
- `$AUTOCODE_DIR/retrospectives/` directory
- `$AUTOCODE_DIR/research/` directory
- `$AUTOCODE_DIR/architectures/v1.md` — initial architecture document based on `autocode_architecture_context`

---

### PGE State Machine

**Applies only when `execution_mode=pge`.**

#### State File: `.omc/state/autocode-pge-state.json`

```json
{
  "active": true,
  "mode": "pge",
  "session_id": "<current_session_id>",
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

#### Phase Transitions

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

#### Plateau Detection (Compound Trigger)

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

#### Hook Integration

- Extends `persistent-mode.mjs` — `autocode-pge-state.json` with `active=true` activates boulder pattern
- Loop continues until phase reaches `terminated`
- Atomic writes on every phase transition via `Write` tool
- Session-scoped ownership prevents cross-session interference

---

### PGE Agent Roles

**Applies only when `execution_mode=pge`.**

#### Core Agents (active every iteration)

| Agent | Model | Role | Input | Output |
|-------|-------|------|-------|--------|
| **Planner** | sonnet | Create experiment plan from architecture + prior results | `architectures/v{N}.md`, `results.tsv`, `lessons/` | `plans/plan_{iter}.md` |
| **Generator** | sonnet | Edit code → run guard → measure metric | plan, target files | commit, metric value, status(keep/discard/crash) |
| **Evaluator** | opus | Analyze results, plateau detection, keep/discard decision | `results.tsv`, recent experiments, code diffs | plateau verdict, retrospective report |

#### On-Demand Agents (spawned at plateau only)

| Agent | Model | Role | Input | Output |
|-------|-------|------|-------|--------|
| **Researcher** | sonnet | Web/codebase search for new optimization techniques | retrospective, current architecture, exhausted directions | `research/research_{N}.md` |
| **Architect** | opus | Redesign architecture based on research + experiment history | research results, `results.tsv`, `architectures/v{N}.md` | `architectures/v{N+1}.md` |

#### Agent Lifecycle

- All agents spawned via `Agent()` tool, fresh each iteration (stateless — clean context window).
- On-demand agents spawned in foreground (need results before continuing).
- Communication is file-based via `.autocode/` directory. No direct messaging.
- See 3P-C and 3P-D for detailed spawn specifications.

---

### Step 3: Run (`/autocode run`)

#### 3-Mode: Mode Detection

1. Read `$PROGRAM_FILE` to determine `execution_mode`.
2. If `execution_mode == "single"`: proceed to **Single Mode (3A-3M)** below.
3. If `execution_mode == "pge"`: proceed to **PGE Mode (3P)** below.

#### Single Mode (3A-3M)

**Applies when `execution_mode=single`.** This is the original autocode experiment loop, unchanged from v1. PIVOT/REFINE/PROCEED logic handles plateau within a fixed architecture.

#### 3A: Pre-flight checks

1. Verify `$PROGRAM_FILE` exists. If not: `program.md not found. Run /autocode init first.`
2. Read `$PROGRAM_FILE` to load configuration (including `max_iterations`, `selected_stages`, limits).
3. Verify target files exist.
4. Verify guard command passes on current code.
5. Load lessons from `$LESSONS_DIR/*.json` if any exist.
6. Create experiment branch: `git checkout -b autocode/{date}` from current branch.

#### 3B: Execution mode selection

Ask the user (via AskUserQuestion):

> How should experiments run?
>
> 1. **Single agent** — One experiment at a time, sequential. Simple and reliable.
> 2. **Single agent + periodic analysis** — Sequential experiments, but every 10 experiments
>    a background analyst agent reviews trends and adjusts strategy.

Store the chosen mode in `$AUTOCODE_DIR/mode.txt` (`single` or `hybrid`).

#### 3C: Establish baseline

1. Run the metric command on unmodified code.
2. Validate metric output is a finite number. If parsing fails, abort with error.
3. Record baseline in `results.tsv`.
4. Initialize counters: `pivot_count=0`, `refine_count=0`, `iteration=1`.
5. Display:
   ```
   Baseline established:
   - {metric_name}: {baseline_value}
   - Branch: autocode/{date}
   - Mode: {single|hybrid}
   - Max iterations: {N} (0 = unlimited)
   - Selected stages: {count} of 23
   - Researchclaw: {available|unavailable}
   - Starting pipeline...
   ```

#### 3D: Pipeline Execution Loop

```
for iteration in 1..max_iterations (or forever if 0):
    load_lessons()  # from $LESSONS_DIR

    for stage in selected_stages:
        execute_stage(stage)

        if stage in quality_gate_stages:
            run_quality_gate(stage)

        if stage == 15:  # RESEARCH_DECISION
            decision = analyze_results()
            handle_decision(decision)

    log_results()
    extract_lessons()
    save_checkpoint()

    if iteration == max_iterations and max_iterations > 0:
        generate_final_summary()
        break
```

#### 3E: Stage Execution

For each stage in `selected_stages`:

**If researchclaw is available**, delegate to the module:
```bash
python -c "from researchclaw.pipeline.executor import execute_stage; execute_stage({stage_id}, config='{program_file}')"
```

**If researchclaw is NOT available**, execute directly in Claude Code:
- Stages 1-2 (Scoping): Analyze target code, decompose into improvement areas.
- Stages 3-6 (Literature): Search codebase for patterns, collect context, screen relevance, extract insights.
- Stages 7-8 (Synthesis): Cluster findings, generate hypotheses for improvement.
- Stages 9-11 (Design): Design experiment, generate code change, plan resource usage.
- Stages 12-13 (Execution): Apply change, run guards and metrics, iterate on failures.
- Stage 14 (Analysis): Compare results against baseline and previous best.
- Stage 15 (Decision): PIVOT/REFINE/PROCEED logic (see 3F).
- Stage 20 (Quality gate): Validate accumulated changes.

**Experiment substeps** (within stages 10-13):

1. **Plan**: Analyze target code. Propose an improvement idea.

   **Strategy progression:**
   - **Early experiments (1-10)**: Systematic exploration. Start with highest-impact areas, try algorithmic improvements, data structure changes, caching, batching, loop optimization.
   - **Mid experiments (11-30)**: Focused exploitation. Double down on successful directions, combine winning changes, look for patterns.
   - **Late experiments (30+)**: Creative exploration. Radical architectural changes, revisit discarded ideas, try opposites.

   **When stuck** (3+ consecutive discards): re-read target code, combine near-misses, switch approach entirely.

2. **Modify**: Edit target file(s). One idea per experiment. Follow existing code style.

3. **Commit**: `git add {target_files} && git commit -m "experiment: {short description}"`

4. **Guard**: Run guard command. If fails, attempt quick fix (max 2 tries). If still failing, log as `crash`, revert, move on.

5. **Measure**: Run metric command, redirect output to log. Validate metric is a finite number.

6. **Decide**:
   - **Improved**: Calculate delta, log as `keep`, update best baseline.
   - **Equal or worse**: Log as `discard`, `git reset --hard HEAD~1`.
   - **Crash**: Log as `crash`, `git reset --hard HEAD~1`.

#### 3F: PIVOT/REFINE/PROCEED Decision Logic

Triggered at Stage 15 (RESEARCH_DECISION) or when metrics stall (3+ consecutive no-improvement iterations).

Analyze recent experiment results:

- **PROCEED**: Metrics are improving. Continue to next stage/iteration.
- **REFINE**: Metrics improving slowly or plateau detected. Incremental adjustment needed.
  - Rollback to Stage 13 (iterative refinement).
  - `refine_count += 1`. Max 2 refines per run.
  - If `refine_count > refine_limit`: force PROCEED.
- **PIVOT**: Metrics stalled or degrading. Strategy change needed.
  - Rollback to Stage 8 (hypothesis generation).
  - `pivot_count += 1`. Max 2 pivots per run.
  - If `pivot_count > pivot_limit`: force PROCEED.

If researchclaw available:
```bash
python -c "from researchclaw.experiment.validator import validate_code; ..."
```

#### 3G: Quality Gates

At configurable stages (default: 5, 9, 20):

1. **Automated assessment**:
   - If researchclaw installed: `python -c "from researchclaw.experiment.validator import validate_code; ..."`
   - If not installed: Claude Code performs inline assessment — guard passes, metric direction correct, no regressions in kept changes.

2. **User approval** (via `AskUserQuestion`):
   - Show current state: iteration, metric value, improvement %, kept/discarded counts.
   - Options: [Approve and continue] [Adjust strategy] [Stop here]
   - If `auto_approve` flag is set in program.md, skip user prompt and auto-approve if guards pass.

#### 3H: Hybrid Mode (Periodic Analysis)

Same as 3D loop, but every 10 experiments, spawn a background Analyst agent:

```
Agent(
  description="Analyze autocode experiment results",
  subagent_type="data-scientist",
  prompt="Read $RESULTS_FILE and logs in $LOGS_DIR/. Analyze:
    1. Which approaches yield the most improvement
    2. Diminishing returns in any direction
    3. Patterns in what works vs fails
    4. Suggested next experiments based on trends
    Write analysis to $ANALYSIS_DIR/analysis_{N}.md",
  run_in_background=true
)
```

**Non-blocking**: Experiment loop continues while analyst runs.

**Feedback integration**: When analyst completes, read analysis before next experiment and adjust strategy.

#### 3I: Self-Learning (MetaClaw-style)

After each iteration (or every N experiments):

1. **Extract lessons** from failures and successes:
   ```json
   {
     "iteration": 5,
     "timestamp": "2026-03-28T12:00:00Z",
     "type": "failure|success|insight",
     "description": "Binary search replacement failed because input is unsorted",
     "action": "Check preconditions before applying algorithmic changes",
     "tags": ["algorithm", "precondition"]
   }
   ```

2. **Store** in `$LESSONS_DIR/lesson_{N}.json`.

3. **Load at start** of each iteration to avoid repeating mistakes.

4. If researchclaw installed: `python -c "from researchclaw.evolution import evolve; ..."`

#### 3J: Checkpoint and Resume Support

After each stage completion, write checkpoint:
```json
{
  "iteration": 5,
  "stage": 12,
  "pivot_count": 1,
  "refine_count": 0,
  "best_metric": 128.9,
  "best_commit": "e5f6g7h",
  "timestamp": "2026-03-28T12:00:00Z"
}
```

Save to `$CHECKPOINT_FILE`. Used by `/autocode resume`.

#### 3K: Simplicity Criterion

All else being equal, simpler is better:
- A tiny improvement that adds ugly complexity -> probably not worth it
- An improvement from deleting code -> definitely keep
- Equal metric but simpler code -> keep

#### 3L: Timeout Handling

If an experiment exceeds the time budget: kill the process, treat as `crash`, revert and move on.

#### 3M: Loop Termination

- **Bounded** (`max_iterations > 0`): Stop after N iterations. Generate final summary.
- **Unlimited** (`max_iterations == 0`): Run until manually interrupted. Never pause to ask "should I continue?".

**Final summary** (generated at termination):
```
## Autocode Final Summary

- Iterations completed: {N}
- Total experiments: {total} ({kept} kept, {discarded} discarded, {crashed} crashed)
- Baseline: {baseline_value} -> Best: {best_value} ({improvement}%)
- Pivots used: {pivot_count}/{pivot_limit}
- Refines used: {refine_count}/{refine_limit}
- Lessons extracted: {lesson_count}

### Top Improvements
1. {description} ({delta}%)
2. ...
```

---

#### PGE Mode (3P)

**Applies when `execution_mode=pge`.** Team-based experiment loop with retrospective-driven architecture redesign.

#### 3P-A: Pre-flight Checks

1-5. Same as Single Mode 3A (verify program.md, read config, verify targets, run guard, load lessons).
6. Create experiment branch: `git checkout -b autocode-pge/{date}` from current branch.
7. Read or create initial architecture: `$AUTOCODE_DIR/architectures/v1.md`.
8. Initialize PGE state file `.omc/state/autocode-pge-state.json` with initial values.

#### 3P-B: Establish Baseline

1. Run the metric command on unmodified code.
2. Validate metric output is a finite number. If parsing fails, abort with error.
3. Record baseline in `results.tsv`.
4. Update state: `best.metric = baseline_value`, `inner_loop.phase = "plan"`.
5. Display:
   ```
   PGE Baseline established:
   - {autocode_metric_name}: {baseline_value}
   - Branch: autocode-pge/{date}
   - Architecture: v1
   - Max iterations: {N} (0 = unlimited)
   - Performance target: {target or "none"}
   - Starting PGE loop...
   ```

#### 3P-C: Inner Loop (Experiments)

```
for each iteration in 1..max_iterations (or forever if 0):
    load_lessons()

    # 1. PLAN
    Update state: phase="plan"
    Spawn Planner agent (sonnet):
      - Read architectures/v{N}.md, results.tsv, lessons/
      - Write plans/plan_{iter}.md

    # 2. GENERATE
    Update state: phase="experiment"
    Spawn Generator agent (sonnet):
      - Read plan, edit target files
      - git commit -m "experiment: {description}"
      - Run guard → fail: retry x2, still fail → crash, revert
      - Run metric command → log to logs/exp_{iter}.log

    # 3. EVALUATE
    Update state: phase="evaluate"
    Spawn Evaluator agent (opus):
      - Judge: keep/discard/crash
        - keep: update best baseline in results.tsv
        - discard: git reset --hard HEAD~1
        - crash: git reset --hard HEAD~1
      - Extract lesson → lessons/lesson_{N}.json
      - Plateau detection (compound trigger):
        plateau = (consecutive_discards >= 3 AND improvement_rate(last_5) < 0.5%)
               OR (consecutive_discards >= 5)

    # 4. BRANCH
    if plateau_detected:
        → Exit inner loop, enter Outer Loop (3P-D)
    elif iteration >= max_iterations and max_iterations > 0:
        → Terminate (3P-F) with reason="budget_exhausted"
    elif best.metric meets performance_target:
        → Terminate (3P-F) with reason="target_reached"
    else:
        → Next iteration
```

#### 3P-D: Outer Loop (Strategic — on plateau)

Triggered when Evaluator detects plateau.

```
# 1. RETROSPECT
Update state: phase="retrospect"
Spawn Evaluator (opus, retrospective mode):
  - Read results.tsv, architectures/v{N}.md, git log
  - Write retrospectives/retro_v{N}.md:
    ## Metric Trend
    ## Effective Patterns
    ## Ineffective Patterns
    ## Exhausted Directions
    ## Remaining Opportunities

# 2. RESEARCH
Update state: phase="research"
Spawn Researcher agent (sonnet):
  - Read retro_v{N}.md, architectures/v{N}.md
  - Web search: optimization techniques, benchmarks
  - Codebase search: similar patterns, unexplored areas
  - Write research/research_{N}.md:
    ## Techniques Found
    ## Codebase Patterns
    ## Recommended New Directions

# 3. REDESIGN
Update state: phase="redesign"
Spawn Architect agent (opus):
  - Read retro, research, results.tsv, architectures/v{N}.md
  - Read program.md → forbidden_zones, immutable_constraints, scope
  - Decision: architecture change promising?
    YES → Write architectures/v{N+1}.md
    NO  → Keep current, update strategy hints only
  - Report: {redesigned: true/false}

# 4. TRANSITION
if redesigned:
    architecture_version += 1, redesign_count += 1
Reset: plateau.detected=false, consecutive_discards=0
→ Check termination (3P-E), then re-enter Inner Loop (3P-C)
```

#### 3P-E: Termination Check

After each outer loop cycle:

- `iteration >= max_iterations` (and max_iterations > 0) → Terminate with reason="budget_exhausted"
- `best.metric` meets `performance_target` → Terminate with reason="target_reached"
- Otherwise → Re-enter Inner Loop (3P-C) with new/updated architecture

#### 3P-F: Termination and Summary

Update state: `active=false`, `inner_loop.phase="terminated"`

Display:
```
## Autocode PGE Final Summary

- Iterations completed: {N}
- Architecture versions: v1 → v{final} ({redesign_count} redesigns)
- Total experiments: {total} ({kept} kept, {discarded} discarded, {crashed} crashed)
- Baseline: {baseline_value} → Best: {best_value} ({improvement}%)
- Termination reason: {budget_exhausted|target_reached}
- Lessons extracted: {lesson_count}

### Architecture Evolution
| Version | Iterations | Best Metric | Improvement | Key Change |
|---------|-----------|-------------|-------------|------------|
| v1      | 1-15      | 132.1       | -9.1%       | (initial)  |
| v2      | 16-35     | 118.4       | -18.5%      | switched to B-tree index |

### Top Improvements
1. {description} ({delta}%)
2. ...
```

---

### Step 4: Status (`/autocode status`)

1. If `$RESULTS_FILE` doesn't exist: `No results yet. Run /autocode init then /autocode run.`

2. Read and parse `results.tsv`, `checkpoint.json`, and mode from `program.md`.

3. **If mode=single**, display:

```
## Autocode Status

**Branch**: autocode/{date}
**Iteration**: {current} / {max_iterations} (0 = unlimited)
**Stage**: {current_stage_name} ({stage_id} of {total_selected})
**Experiments**: {total} total ({kept} kept, {discarded} discarded, {crashed} crashed)
**Best metric**: {best_value} (baseline: {baseline_value}, improvement: {pct}%)
**Pivots**: {pivot_count}/{pivot_limit}  |  **Refines**: {refine_count}/{refine_limit}
**Researchclaw**: {available|unavailable}
**Lessons learned**: {lesson_count}
```

4. **If mode=pge**, read `.omc/state/autocode-pge-state.json` and display:

```
## Autocode PGE Status

**Branch**: autocode-pge/{date}
**Mode**: PGE (Plan-Generate-Execute)
**Phase**: {current phase from state}
**Architecture**: v{version} ({redesign_count} redesigns)
**Iteration**: {current} / {max_iterations} (0 = unlimited)
**Experiments**: {total} total ({kept} kept, {discarded} discarded, {crashed} crashed)
**Best metric**: {best_value} (baseline: {baseline_value}, improvement: {pct}%)
**Performance target**: {target or "none"} — {reached or "not yet"}
**Plateau**: {detected or "not detected"} (consecutive discards: {N})
**Lessons learned**: {lesson_count}

### Architecture Evolution
| Version | Iterations | Best Metric | Key Change |
|---------|-----------|-------------|------------|
| v1      | 1-15      | 132.1       | (initial)  |
| v2      | 16-35     | 118.4       | switched to B-tree index |
```

5. If experiments are currently running, also show time elapsed and experiments per hour.

---

### Step 5: Resume (`/autocode resume`)

1. Verify `$PROGRAM_FILE`, `$RESULTS_FILE`, and `$CHECKPOINT_FILE` exist.
   If not: `No checkpoint found. Run /autocode init then /autocode run first.`
2. Read mode from `program.md`.

**If mode=single:**

3. Read checkpoint to restore state: iteration, stage, pivot/refine counts, best metric.
4. Load lessons from `$LESSONS_DIR`.
5. Detect the experiment branch and verify it's checked out.
6. Display:
   ```
   Resuming autocode (single mode):
   - Branch: autocode/{date}
   - Iteration: {current}/{max_iterations}
   - Stage: {stage_name} ({stage_id})
   - Current best: {autocode_metric_name}: {value}
   - Resuming pipeline...
   ```
7. Continue the pipeline loop (3A-3M) from the checkpointed stage and iteration.

**If mode=pge:**

3. Read PGE state from `.omc/state/autocode-pge-state.json`.
4. Load lessons from `$LESSONS_DIR`.
5. Detect the experiment branch (`autocode-pge/{date}`) and verify it's checked out.
6. Display:
   ```
   Resuming autocode (PGE mode):
   - Branch: autocode-pge/{date}
   - Phase: {current phase}
   - Architecture: v{version}
   - Iteration: {current}/{max_iterations}
   - Current best: {autocode_metric_name}: {value}
   - Redesigns: {redesign_count}
   - Resuming PGE loop...
   ```
7. Continue the PGE loop from the checkpointed phase:
   - `plan` or `experiment`: re-enter Inner Loop (3P-C)
   - `retrospect`, `research`, or `redesign`: re-enter Outer Loop (3P-D)
   - `terminated`: report final summary and exit

---

## File Structure

```
.autocode/
├── program.md                    # init output (unified schema)
├── results.tsv                   # full experiment log (append-only)
├── mode.txt                      # single | pge
├── checkpoint.json               # resume state
├── lessons/
│   ├── lesson_001.json           # self-learning entries
│   └── lesson_002.json
├── logs/                         # experiment stdout/stderr
├── analysis/                     # hybrid mode analyst reports (single mode)
├── plans/                        # [PGE] per-iteration experiment plans
│   ├── plan_001.md
│   └── plan_002.md
├── architectures/                # [PGE] versioned architecture documents
│   ├── v1.md
│   ├── v2.md
│   └── v3.md
├── retrospectives/               # [PGE] architecture retrospectives
│   ├── retro_v1.md
│   └── retro_v2.md
└── research/                     # [PGE] researcher outputs
    ├── research_001.md
    └── research_002.md

.omc/state/
└── autocode-pge-state.json       # [PGE] loop orchestration state
```

---

## Tool Usage

| Phase | Tool | Purpose |
|-------|------|---------|
| Install | `Bash` | Clone repo, pip install, verify import |
| Init questions | `AskUserQuestion` | Brainstorming-pattern HITL interview (one at a time) |
| Stage selection | `AskUserQuestion` (multiSelect) | Choose pipeline stages |
| Init confirmation | `AskUserQuestion` | Approve/edit program.md |
| Mode selection | `AskUserQuestion` | Choose single or PGE execution mode |
| Quality gates | `AskUserQuestion` | User approval at gate stages (unless auto-approve) |
| Code analysis | `Read`, `Grep`, `Glob` | Analyze target files |
| Code modification | `Edit` | Modify target files |
| Running experiments | `Bash` | Execute metric/guard commands (redirect to logs) |
| Researchclaw calls | `Bash` | Delegate to researchclaw Python modules |
| Metric extraction | `Bash` | Extract and validate metric |
| Results logging | `Edit` or `Bash` | Append to results.tsv |
| Checkpoint | `Write` | Save checkpoint.json / autocode-pge-state.json |
| Lessons | `Write` | Save lesson JSON files |
| Periodic analysis | `Agent(run_in_background=true)` | Hybrid mode: analyze trends (single mode) |
| **PGE: Planner** | `Agent(model="sonnet")` | Plan next experiment based on architecture |
| **PGE: Generator** | `Agent(model="sonnet")` | Execute experiment (edit, guard, measure) |
| **PGE: Evaluator** | `Agent(model="opus")` | Judge results, detect plateau, write retrospective |
| **PGE: Researcher** | `Agent(model="sonnet")` | Search for new optimization techniques |
| **PGE: Architect** | `Agent(model="opus")` | Redesign architecture based on research |
| **PGE: State** | `Write` | Atomic state writes to autocode-pge-state.json |

## Key Principles

**Core (both modes):**
- **Single measurable metric** — no metric = no autocode.
- **Guard before accept** — tests/lint must pass. Never keep broken code.
- **Git as checkpoint** — every experiment is a commit. Easy to review, revert, cherry-pick.
- **Simplicity criterion** — complexity cost weighed against improvement magnitude.
- **Bounded by default** — `max_iterations` is the only hard limit (default 10). Prevents runaway loops.
- **Self-learning** — extract lessons from failures, load in future iterations.
- **Graceful degradation** — full pipeline with researchclaw, basic loop without it.
- **Checkpoint and resume** — never lose progress. Resume from any interruption point.
- **program.md is portable** — can be used with any AI agent, not just Claude Code.
- **.autocode/ is ephemeral** — gitignored, project-local, disposable.

**PGE-specific:**
- **Architecture evolution** — plateau triggers redesign, not just parameter tweaking.
- **Stateless agents** — fresh context per spawn prevents pollution across iterations.
- **File-based communication** — agents communicate via `.autocode/` files, not messages.
- **Compound plateau detection** — multiple signals prevent false triggers.
- **Versioned architectures** — every redesign is a new document. Compare, rollback, learn.
- **Hook persistence** — boulder pattern via `autocode-pge-state.json` ensures loop survives compaction.
