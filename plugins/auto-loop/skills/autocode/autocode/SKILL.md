---
name: autocode
description: "Autonomous code improvement loop with optional 23-stage research pipeline (AutoResearchClaw). Subcommands: install (researchclaw), init [N] (max iterations, default 10, 0=unlimited), run (execute pipeline), status (progress), resume (checkpoint). Features: PIVOT/REFINE decision logic, quality gates, self-learning from failures, stage selection UI. Falls back to direct Claude Code execution when researchclaw is not installed."
argument-hint: "<subcommand: install|init|run|status|resume> [iterations]"
---

# Autocode — Autonomous Code Improvement

Autonomous experiment loop for code improvement with an optional 23-stage research pipeline.
Modify target code, measure metrics, keep improvements, discard regressions. Supports bounded
iteration counts, quality gates, PIVOT/REFINE decision logic, and self-learning from past failures.

Built on [AutoResearchClaw](https://github.com/aiming-lab/AutoResearchClaw) when installed;
falls back to direct Claude Code execution otherwise.

Inspired by [autoresearch](https://github.com/karpathy/autoresearch) — same pattern, generalized beyond ML training.

> **For ML-specific research** (model training, hyperparameter tuning, architecture experiments), use `/auto_research` instead. It includes deep-interview initialization, ML domain knowledge, and experiment categorization.

## Subcommands

| Command | Action | User Confirmation |
|---------|--------|-------------------|
| `/autocode install` | Clone AutoResearchClaw + pip install | Not needed |
| `/autocode init [N]` | Interactive setup, generate `program.md`. N = max iterations (default 10, 0 = unlimited) | Required |
| `/autocode run` | Execute pipeline based on `program.md` | Not needed (autonomous) |
| `/autocode status` | Show progress, stage, iteration count | Not needed |
| `/autocode resume` | Resume from checkpoint | Not needed |

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

#### 2B: Gather Information

Ask the user these questions (use `AskUserQuestion` for each):

1. **Target**: What file(s) should the agent modify?
   - Example: `src/parser.py`, `lib/engine.ts`
   - Recommend: single file or small module for best results

2. **Metric**: How do we measure success? (must be a single number, lower or higher is better)
   - Performance: `pytest-benchmark` output, request latency, throughput
   - Size: bundle size, binary size, memory usage
   - Quality: test count, lint warning count, type coverage %
   - Custom: any command that outputs a number

3. **Metric command**: The exact shell command to extract the metric number.
   - Example: `pytest --benchmark-only --benchmark-json=bench.json && python -c "import json; print(json.load(open('bench.json'))['benchmarks'][0]['stats']['mean'])"`
   - Example: `wc -c dist/bundle.js | awk '{print $1}'`

4. **Direction**: Is lower better or higher better?
   - `lower` = minimize (latency, bundle size, error count)
   - `higher` = maximize (throughput, test coverage, score)

5. **Guard command**: What must pass before we accept a change? (tests, lint, type check)
   - Example: `pytest && mypy src/`
   - Can be empty if no guards needed

6. **Time budget per experiment** (optional, default: 2 minutes)

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

```markdown
# Autocode Program

## Target

- **Files to modify**: {target_files}
- **Read-only context**: {any files the agent should read but not modify}

## Metric

- **Command**: `{metric_command}`
- **Direction**: {lower|higher} is better
- **Name**: {metric_name} (e.g., "latency_ms", "bundle_bytes", "test_count")

## Guard

Before accepting any change, this must pass:
```
{guard_command}
```

## Constraints

- **Time budget**: {time_budget} per experiment
- **Do NOT**: {any restrictions}

## Strategy hints

{Optional section}

## Pipeline Configuration

- **max_iterations**: {N}
- **selected_stages**: [{list of stage IDs}]
- **pivot_limit**: 2
- **refine_limit**: 2
- **researchclaw_available**: {true|false}
- **quality_gate_stages**: [5, 9, 20]
- **lessons_enabled**: true
```

Also initialize:
- `$AUTOCODE_DIR/results.tsv` with header: `iteration\tstage\tcommit\tmetric\tstatus\tdescription\tdelta`
- `$AUTOCODE_DIR/logs/` directory
- `$AUTOCODE_DIR/analysis/` directory
- `$AUTOCODE_DIR/lessons/` directory
- `$AUTOCODE_DIR/checkpoint.json` with initial state

Add `.autocode/` to `.gitignore` if not already there (ask user first).

Present the generated program.md via `AskUserQuestion` with options:
[Approve and save] [Edit and regenerate] [Start over]

---

### Step 3: Run (`/autocode run`)

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

### Step 4: Status (`/autocode status`)

1. If `$RESULTS_FILE` doesn't exist: `No results yet. Run /autocode init then /autocode run.`

2. Read and parse `results.tsv` and `checkpoint.json`.

3. Display summary:

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

### Experiment History
| # | Iter | Stage | Commit | Metric | Status | Description | Delta |
|---|------|-------|--------|--------|--------|-------------|-------|
| 1 | 1 | 12 | a1b2c3d | 145.3 | keep | baseline | -- |
| 2 | 1 | 12 | b2c3d4e | 132.1 | keep | binary search | -9.1% |
...

### Kept Changes (cumulative)
1. replace linear search with binary search (-9.1%)
2. eliminate redundant copies (-2.4%)

Total improvement: -11.3% from baseline
```

4. If experiments are currently running, also show time elapsed and experiments per hour.

---

### Step 5: Resume (`/autocode resume`)

1. Verify `$PROGRAM_FILE`, `$RESULTS_FILE`, and `$CHECKPOINT_FILE` exist.
   If not: `No checkpoint found. Run /autocode init then /autocode run first.`
2. Read checkpoint to restore state: iteration, stage, pivot/refine counts, best metric.
3. Load lessons from `$LESSONS_DIR`.
4. Detect the experiment branch and verify it's checked out.
5. Read execution mode from `$AUTOCODE_DIR/mode.txt` (default: `single` if missing).
6. Display:
   ```
   Resuming autocode:
   - Branch: autocode/{date}
   - Iteration: {current}/{max_iterations}
   - Stage: {stage_name} ({stage_id})
   - Current best: {metric_name}: {value}
   - Pivots: {pivot_count}/{pivot_limit}
   - Refines: {refine_count}/{refine_limit}
   - Lessons loaded: {count}
   - Mode: {single|hybrid}
   - Resuming pipeline...
   ```
7. Continue the pipeline loop (3D) from the checkpointed stage and iteration.

---

## Tool Usage

| Phase | Tool | Purpose |
|-------|------|---------|
| Install | `Bash` | Clone repo, pip install, verify import |
| Init questions | `AskUserQuestion` | Gather target, metric, guard, constraints |
| Stage selection | `AskUserQuestion` (multiSelect) | Choose pipeline stages |
| Init confirmation | `AskUserQuestion` | Approve/edit program.md |
| Mode selection | `AskUserQuestion` | Choose single or hybrid execution mode |
| Quality gates | `AskUserQuestion` | User approval at gate stages (unless auto-approve) |
| Code analysis | `Read`, `Grep`, `Glob` | Analyze target files before proposing experiments |
| Code modification | `Edit` | Modify target files with experimental changes |
| Running experiments | `Bash` | Execute metric/guard commands (redirect output to logs) |
| Researchclaw calls | `Bash` | Delegate to researchclaw Python modules when available |
| Metric extraction | `Bash` | Extract and validate metric from log files |
| Results logging | `Edit` or `Bash` | Append to results.tsv |
| Checkpoint | `Write` | Save checkpoint.json after each stage |
| Lessons | `Write` | Save lesson JSON files |
| Periodic analysis | `Agent(subagent_type="data-scientist", run_in_background=true)` | Hybrid mode: analyze trends every 10 experiments |
| Analysis reading | `Read` | Read analyst output to adjust strategy |

## Key Principles

- **Single measurable metric** — the core requirement. No metric = no autocode.
- **Guard before accept** — tests/lint must pass. Never keep broken code.
- **Git as checkpoint** — every experiment is a commit. Easy to review, revert, cherry-pick.
- **Simplicity criterion** — complexity cost must be weighed against improvement magnitude.
- **Bounded by default** — 10 iterations unless overridden. Prevents runaway loops.
- **Adaptive strategy** — shift from systematic exploration to focused exploitation based on results.
- **PIVOT/REFINE/PROCEED** — structured decision logic prevents thrashing. Max 2 pivots, 2 refines.
- **Quality gates** — automated + human checkpoints at configurable stages.
- **Self-learning** — extract lessons from failures, load them in future iterations to avoid repeating mistakes.
- **Graceful degradation** — full pipeline with researchclaw, basic loop without it. Always works.
- **Checkpoint and resume** — never lose progress. Resume from any interruption point.
- **Hybrid mode** — periodic background analysis improves strategy without blocking the experiment loop.
- **Stage selection** — user controls which pipeline stages run. Paper writing stages off by default.
- **Redirect output** — never let experiment output flood the context window. Log to files, extract metrics via grep.
- **Validate metrics** — always check that extracted metrics are finite numbers before comparing.
- **program.md is portable** — can be used with any AI agent, not just Claude Code.
- **results.tsv is the log** — untracked by git, append-only record of all experiments.
- **.autocode/ is ephemeral** — gitignored, project-local, disposable.
