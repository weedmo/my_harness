---
name: auto_research
description: "Autonomous ML research loop with deep-interview initialization and optional 23-stage research pipeline (AutoResearchClaw). Subcommands: install (researchclaw), init [N] (max iterations, default 10, 0=unlimited), run (execute pipeline), status (progress), analyze (trends), resume (checkpoint). Features: PIVOT/REFINE decision logic, quality gates, self-learning, stage selection UI, literature search, multi-agent debate. Falls back to direct Claude Code execution when researchclaw is not installed."
argument-hint: "<subcommand: install|init|run|status|analyze|resume> [iterations]"
---

# Auto Research — Autonomous ML Research

Autonomous experiment loop for ML research with an optional 23-stage research pipeline.
Analyze an ML repository, design experiments informed by domain knowledge, modify training code,
measure metrics, keep improvements, discard regressions. Supports bounded iteration counts,
quality gates, PIVOT/REFINE decision logic, literature search, and self-learning from past failures.

Built on [AutoResearchClaw](https://github.com/aiming-lab/AutoResearchClaw) when installed;
falls back to direct Claude Code execution with ML domain knowledge otherwise.

Inspired by [Karpathy's autoresearch](https://github.com/karpathy/autoresearch) — specialized for ML
research with deep-interview initialization and adaptive experiment strategy.

## Subcommands

| Command | Action | User Confirmation |
|---------|--------|-------------------|
| `/auto_research install` | Clone AutoResearchClaw + pip install | Not needed |
| `/auto_research init [N]` | Deep-interview -> generate `research_program.md`. N = max iterations (default 10, 0 = unlimited) | Required (interview) |
| `/auto_research run` | Execute pipeline based on `research_program.md` | Execution mode selection |
| `/auto_research status` | Show progress, stage, iteration count | Not needed |
| `/auto_research analyze` | Deep analysis of experiment trends | Not needed |
| `/auto_research resume` | Resume from checkpoint | Not needed |

## Procedure

### Step 0: Detect Project Root and Researchclaw

```
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
RESEARCH_DIR="$PROJECT_ROOT/.auto_research"
PROGRAM_FILE="$RESEARCH_DIR/research_program.md"
RESULTS_FILE="$RESEARCH_DIR/results.tsv"
LOGS_DIR="$RESEARCH_DIR/logs"
ANALYSIS_DIR="$RESEARCH_DIR/analysis"
LESSONS_DIR="$RESEARCH_DIR/lessons"
CHECKPOINT_FILE="$RESEARCH_DIR/checkpoint.json"
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
- `analyze` -> **Analyze workflow** (Step 5)
- `resume` -> **Resume workflow** (Step 6)

Parse iteration count from args: `/auto_research init 10` -> `max_iterations=10`. Default: 10. If 0: unlimited (legacy infinite loop).

---

### Step 1A: Install (`/auto_research install`)

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

4. Print result: `AutoResearchClaw installed successfully. Full pipeline with literature search, experiment sandbox, and multi-agent debate now available.`

---

### Step 2: Init — Deep Interview (`/auto_research init [N]`)

#### Phase 2A: Parse Iteration Count

Extract N from arguments. Examples:
- `/auto_research init` -> `max_iterations=10`
- `/auto_research init 20` -> `max_iterations=20`
- `/auto_research init 0` -> `max_iterations=0` (unlimited)

#### Phase 2B: Repository Reconnaissance

Before asking the user anything, scan the repo to gather facts autonomously:

1. **Detect ML framework**: PyTorch, TensorFlow, JAX, HuggingFace, Lightning, etc.
2. **Identify key files**:
   - Training scripts (train.py, main.py, run_*.py)
   - Model definitions (model.py, architecture files)
   - Config files (config.yaml, hparams.yaml, hydra configs)
   - Data pipeline (dataset.py, dataloader, prepare.py)
   - Evaluation scripts (eval.py, test.py, benchmark scripts)
3. **Extract current metrics**: Look for logged metrics, wandb/tensorboard configs, evaluation functions
4. **Detect constraints**: GPU requirements, dependencies, data paths
5. **Read README and docs**: Understand the project's purpose

If researchclaw available:
```bash
python -c "from researchclaw.domains.detector import detect_domain; print(detect_domain('$PROJECT_ROOT'))"
```

Store findings as `recon_context`. This prevents asking the user questions the code already answers.

#### Phase 2C: Deep Interview Loop

Initialize interview state and persist to `$RESEARCH_DIR/interview_state.json`:

```json
{
  "interview_id": "<uuid>",
  "type": "ml_research",
  "initial_recon": "<recon_context summary>",
  "rounds": [],
  "current_ambiguity": 1.0,
  "threshold": 0.2,
  "challenge_modes_used": []
}
```

Update this file after every round so interrupted interviews can resume.
If `$RESEARCH_DIR/interview_state.json` exists when `init` is invoked, ask:
"Previous interview found ({N} rounds, ambiguity {score}%). Resume or restart?"

Announce:

> Starting research interview. I've scanned your repo and found: {recon_summary}.
> I'll ask targeted questions to define the research program. Ambiguity: 100%

**Clarity Dimensions for ML Research** (weighted scoring):

| Dimension | Weight | What it measures |
|-----------|--------|-----------------|
| Research Goal | 0.30 | What metric to optimize, what constitutes success |
| Experiment Scope | 0.25 | Which files to modify, what's off-limits |
| Evaluation Protocol | 0.25 | How to measure, baseline, comparison method |
| Resource Constraints | 0.20 | GPU budget, time per experiment, VRAM limits |

**Ambiguity formula:**
`ambiguity = 1 - (goal * 0.30 + scope * 0.25 + evaluation * 0.25 + resources * 0.20)`

**Rules:**
- Ask ONE question per round via `AskUserQuestion`, targeting the weakest dimension
- Use recon_context to ask informed questions — never ask what the code reveals
- Score ambiguity after every answer, display transparently
- Proceed to spec generation when ambiguity <= 0.2
- Round 4+: Allow early exit. Round 8: Soft warning. Round 15: Hard cap.

**Challenge modes** (used once each):
- **Round 4+: Contrarian** — "Do you actually need to change the architecture, or could a learning rate sweep get you 80% of the way?"
- **Round 6+: Simplifier** — "What's the minimum viable experiment that would tell you if this research direction is worth pursuing?"

#### Phase 2D: Stage Selection UI

After interview completes, present 23-stage pipeline via `AskUserQuestion` with multiSelect.

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
| 16 | G: Paper Writing | Outline | ON |
| 17 | G: Paper Writing | Draft | ON |
| 18 | G: Paper Writing | Peer review | ON |
| 19 | G: Paper Writing | Revision | ON |
| 20 | H: Finalization | Quality gate (GATE) | ON |
| 21 | H: Finalization | Archive results | ON |
| 22 | H: Finalization | Export artifacts | ON |
| 23 | H: Finalization | Citation verification | ON |

**auto_research defaults**: ALL 23 stages ON. User can deselect unwanted stages.

#### Phase 2E: Generate research_program.md

```markdown
# Auto Research Program

## Metadata
- Interview ID: {uuid}
- Final Ambiguity: {score}%
- Generated: {timestamp}
- ML Framework: {framework}

## Research Goal
- **Primary metric**: {metric_name} (e.g., val_bpb, val_accuracy, mAP)
- **Direction**: {lower|higher} is better
- **Success threshold**: {target value, if any}
- **Secondary metrics**: {optional — e.g., VRAM, throughput, inference latency}

## Experiment Scope
- **Files to modify**: {editable files}
- **Read-only context**: {files to read but not modify}
- **Off-limits**: {files/modules that must not be changed}

## Evaluation Protocol
- **Metric command**: `{command to extract primary metric}`
- **Resource command**: `{command to extract VRAM/time/etc}`
- **Guard command**: `{tests/checks that must pass}`
- **Time budget**: {minutes per experiment}

## Resource Constraints
- **GPU**: {detected or specified}
- **VRAM policy**: {strict limit | soft limit with threshold | no limit}
- **Dependency policy**: {no new deps | allow with user approval}

## Strategy
- **Priority areas**: {what to try first, from interview}
- **Hints**: {user-provided strategy hints}
- **Avoid**: {explicitly excluded approaches}

## Experiment Taxonomy
1. **hp_tune** — LR, batch size, weight decay, scheduler
2. **arch** — layers, width, attention, normalization
3. **optim** — optimizer type, momentum, adaptive methods
4. **reg** — dropout, augmentation, label smoothing
5. **dynamics** — warmup, cooldown, gradient clipping, accumulation
6. **data** — preprocessing, tokenization, batching strategy
7. **novel** — ideas from papers, combinations of above

## Pipeline Configuration
- **max_iterations**: {N}
- **selected_stages**: [{list of all 23 stage IDs by default}]
- **pivot_limit**: 2
- **refine_limit**: 2
- **researchclaw_available**: {true|false}
- **quality_gate_stages**: [5, 9, 20]
- **lessons_enabled**: true
- **auto_approve_gates**: false
- **experiment_mode**: sandbox
```

Also initialize:
- `$RESEARCH_DIR/results.tsv` with header: `iteration\tstage\tcommit\tmetric\tmemory_gb\ttime_sec\tstatus\tcategory\tdescription\tdelta`
- `$RESEARCH_DIR/logs/`, `$RESEARCH_DIR/analysis/`, `$RESEARCH_DIR/lessons/` directories
- `$RESEARCH_DIR/checkpoint.json` with initial state

Add `.auto_research/` to `.gitignore` if not already there.
Delete `$RESEARCH_DIR/interview_state.json` after successful save.

Present via `AskUserQuestion`: [Approve and save] [Edit and regenerate] [Restart interview]

---

### Step 3: Run (`/auto_research run`)

#### 3A: Pre-flight

1. Verify `$PROGRAM_FILE` exists. If not: `research_program.md not found. Run /auto_research init first.`
2. Read `$PROGRAM_FILE` to load all configuration.
3. Verify target files and metric commands work.
4. Load lessons from `$LESSONS_DIR/*.json` if any exist.
5. Create experiment branch: `git checkout -b auto_research/{date}`

#### 3B: Execution Mode Selection

Ask the user (via AskUserQuestion):

> How should experiments run?
>
> 1. **Single agent** — One experiment at a time, sequential. (~12 experiments/hour at 5min each)
> 2. **Single agent + periodic analysis** — Sequential experiments, every 10 experiments an analyst reviews trends.
> 3. **Multi-agent research org** — Strategist + Experimenter(s) + Analyst in parallel.

Store mode in `$RESEARCH_DIR/mode.txt`.

#### 3C: Establish Baseline

1. Run the metric command on unmodified code.
2. Record baseline in `results.tsv`.
3. Initialize counters: `pivot_count=0`, `refine_count=0`, `iteration=1`.
4. Display:
   ```
   Baseline established:
   - {metric_name}: {baseline_value}
   - VRAM: {memory_gb} GB
   - Branch: auto_research/{date}
   - Mode: {single|multi-agent|hybrid}
   - Max iterations: {N} (0 = unlimited)
   - Selected stages: {count} of 23
   - Researchclaw: {available|unavailable}
   - Starting pipeline...
   ```

#### 3D: Pipeline Execution Loop

```
for iteration in 1..max_iterations (or forever if 0):
    load_lessons()

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

**If researchclaw is available**, delegate to modules:

| Stages | Module |
|--------|--------|
| 1-2 | `researchclaw.pipeline.stage_impls._topic` |
| 3-6 | `researchclaw.literature.search` + `researchclaw.pipeline.stage_impls._literature` |
| 7-8 | `researchclaw.pipeline.stage_impls._synthesis` |
| 9-11 | `researchclaw.pipeline.stage_impls._experiment_design` + `researchclaw.agents.benchmark_agent` |
| 10 | `researchclaw.pipeline.stage_impls._code_generation` (CodeAgent multi-phase) |
| 12-13 | `researchclaw.experiment.runner` + `researchclaw.experiment.sandbox` |
| 14-15 | `researchclaw.pipeline.stage_impls._analysis` |
| 16-19 | `researchclaw.pipeline.stage_impls._paper_writing` |
| 20-23 | `researchclaw.pipeline.stage_impls._review_publish` |

**If researchclaw is NOT available**, execute directly in Claude Code with ML domain knowledge:

- Stages 1-2: Analyze ML repo structure, decompose research goal into sub-problems.
- Stages 3-6: Search codebase for patterns, web search for papers (if available), collect relevant techniques.
- Stages 7-8: Synthesize findings, generate experiment hypotheses by taxonomy category.
- Stages 9-11: Design experiment plan, generate code change, assess GPU/VRAM requirements.
- Stages 12-13: Apply code change, run training/eval, track VRAM. Self-heal on NaN/crash.
- Stage 14: Multi-dimensional analysis (metric + VRAM + time).
- Stage 15: PIVOT/REFINE/PROCEED decision.
- Stages 16-19: Generate paper outline, draft sections, run peer review debate, revise.
- Stage 20: Quality gate — 4-layer verification.
- Stages 21-23: Archive to knowledge base, export LaTeX/Markdown, verify citations.

**Experiment substeps** (within stages 10-13):

1. **Plan**: Use ML domain knowledge + experiment taxonomy. Categorize as `hp_tune|arch|optim|reg|dynamics|data|novel`.
2. **Modify**: Edit target files. One idea per experiment. Follow existing code style.
3. **Commit**: `git add {files} && git commit -m "experiment: [{category}] {description}"`
4. **Guard**: Run guard command. Quick fix (max 2 tries). If still failing: crash, revert.
5. **Measure**: Run metric + resource commands. Track VRAM alongside primary metric.
6. **Decide**: Improved -> keep. Equal/worse -> discard + revert. Crash -> revert.

#### 3F: PIVOT/REFINE/PROCEED Decision Logic

Triggered at Stage 15 or when metrics stall (3+ consecutive no-improvement).

- **PROCEED**: Metrics improving. Continue.
- **REFINE**: Plateau detected. Rollback to Stage 13. `refine_count += 1`. Max 2.
- **PIVOT**: Stalled/degrading. Rollback to Stage 8. `pivot_count += 1`. Max 2.

If researchclaw available, use `researchclaw.pipeline.stage_impls._analysis` for decision.

#### 3G: Quality Gates

At stages 5, 9, 20:

1. **Automated assessment**: researchclaw validator (if installed) or Claude Code inline check.
2. **User approval** via `AskUserQuestion` (unless `auto_approve_gates: true`):
   - Show: iteration, metric, improvement %, category breakdown.
   - Options: [Approve] [Adjust strategy] [Stop]

#### 3H: Self-Learning (MetaClaw-style)

After each iteration:

1. **Extract lessons**:
   ```json
   {
     "iteration": 5,
     "type": "failure|success|insight",
     "category": "hp_tune",
     "description": "LR 0.1 caused divergence with batch size 32",
     "action": "Keep LR below 0.05 when batch size < 64",
     "tags": ["lr", "batch_size", "divergence"]
   }
   ```

2. **Store** in `$LESSONS_DIR/lesson_{N}.json`.
3. **Load** at start of each iteration to inform experiment selection.
4. If researchclaw installed: `python -c "from researchclaw.evolution import evolve; ..."`

#### 3I: Checkpoint and Resume

After each stage, write `checkpoint.json`:
```json
{
  "iteration": 3,
  "stage": 14,
  "pivot_count": 1,
  "refine_count": 0,
  "best_metric": 0.823,
  "best_commit": "a1b2c3d",
  "best_vram_gb": 18.2,
  "timestamp": "2026-03-28T12:00:00Z"
}
```

#### 3J: Loop Termination

- **Bounded** (`max_iterations > 0`): Stop after N iterations. Generate final summary.
- **Unlimited** (`max_iterations == 0`): Run until manually interrupted.

**Final summary**:
```
## Auto Research Final Summary

- Iterations completed: {N}
- Total experiments: {total} ({kept} kept, {discarded} discarded, {crashed} crashed)
- Baseline: {baseline} -> Best: {best} ({improvement}%)
- Peak VRAM: {max_vram} GB
- Pivots: {pivot_count}/{pivot_limit}
- Refines: {refine_count}/{refine_limit}
- Lessons extracted: {lesson_count}

### By Category
| Category | Tried | Kept | Success Rate | Avg Delta |
|----------|-------|------|-------------|-----------|

### Top Improvements
1. [{category}] {description} ({delta}%)
2. ...
```

---

### Step 4: Status (`/auto_research status`)

1. If `$RESULTS_FILE` doesn't exist: `No results yet. Run /auto_research init then /auto_research run.`

2. Read `results.tsv` and `checkpoint.json`.

3. Display:

```
## Auto Research Status

**Branch**: auto_research/{date}
**Iteration**: {current} / {max_iterations}
**Stage**: {current_stage_name} ({stage_id})
**Experiments**: {total} ({kept} kept, {discarded} discarded, {crashed} crashed)
**Best metric**: {best_value} (baseline: {baseline_value}, improvement: {pct}%)
**Peak VRAM**: {max_vram} GB
**Pivots**: {pivot_count}/{pivot_limit}  |  **Refines**: {refine_count}/{refine_limit}
**Researchclaw**: {available|unavailable}
**Lessons**: {lesson_count}

### By Category
| Category | Tried | Kept | Success Rate | Avg Delta |
|----------|-------|------|-------------|-----------|

### Experiment History (last 10)
| # | Iter | Stage | Commit | Metric | VRAM | Time | Status | Category | Description | Delta |
```

---

### Step 5: Analyze (`/auto_research analyze`)

Deep analysis of experiment results.

1. Read all of `results.tsv` and available experiment logs.

2. If researchclaw available:
   ```bash
   python -c "from researchclaw.pipeline.stage_impls._analysis import analyze; ..."
   ```

3. Generate analysis covering:
   - **Trend Analysis**: Best categories, diminishing returns, trajectory
   - **Failure Patterns**: Consistent failures, crash concentration, common errors
   - **Strategy Recommendations**: Explore further vs abandon
   - **Resource Analysis**: VRAM trend, time efficiency, cost-benefit

4. Write to `$ANALYSIS_DIR/analysis_{timestamp}.md`.
5. Display key insights.

---

### Step 6: Resume (`/auto_research resume`)

1. Verify `$PROGRAM_FILE`, `$RESULTS_FILE`, and `$CHECKPOINT_FILE` exist.
2. Read checkpoint to restore state.
3. Load lessons from `$LESSONS_DIR`.
4. Detect experiment branch, verify checkout.
5. Display:
   ```
   Resuming auto_research:
   - Branch: auto_research/{date}
   - Iteration: {current}/{max_iterations}
   - Stage: {stage_name} ({stage_id})
   - Current best: {metric}: {value}
   - VRAM: {vram} GB
   - Pivots: {pivot_count}/{pivot_limit}
   - Refines: {refine_count}/{refine_limit}
   - Lessons loaded: {count}
   - Mode: {single|hybrid|multi-agent}
   - Resuming pipeline...
   ```
6. Continue pipeline loop from checkpointed state.

---

## ML Domain Knowledge

The experiment strategist should draw on these patterns when deciding what to try.

### General Principles
- **Learning rate is king**: Often the single most impactful hyperparameter. Try it first.
- **Batch size and LR co-scale**: When increasing batch size, scale LR proportionally.
- **Regularization after optimization**: Get the optimizer working before adding regularization.
- **Simpler baselines first**: Ensure basic hyperparameters are tuned before novel techniques.
- **One change at a time**: Isolate variables to understand what works.

### By ML Domain

**LLM / Language Models**:
- Architecture: attention patterns, positional encoding (RoPE, ALiBi), normalization (RMSNorm)
- Optimization: AdamW, Muon, learning rate warmup/cooldown schedules
- Scaling: depth vs width tradeoff, aspect ratio
- Efficiency: Flash Attention, sliding window, GQA/MQA

**Computer Vision**:
- Architecture: backbone (ResNet, ViT, ConvNeXt), neck, head design
- Augmentation: mixup, cutout, RandAugment, mosaic
- Training: cosine LR, warmup epochs, EMA
- Resolution: progressive resizing, multi-scale training

**Reinforcement Learning**:
- Hyperparameters: discount factor, GAE lambda, clip ratio, entropy coefficient
- Architecture: shared vs separate actor-critic, network width/depth
- Training: batch size, epochs per update, normalization
- Exploration: epsilon schedule, intrinsic motivation

**Robotics / Control**:
- Sim-to-real: domain randomization parameters
- Architecture: proprioception encoding, action space design
- Training: curriculum learning, reward shaping
- Evaluation: success rate, trajectory quality metrics

### Paper-Informed Strategy

When web search is available and the agent is stuck or in late-stage exploration:
1. Search for recent papers relevant to the model architecture or training method
2. Look for techniques that improved similar baselines
3. Adapt promising ideas to the current codebase
4. Credit the source in the experiment description

---

## Tool Usage

| Phase | Tool | Purpose |
|-------|------|---------|
| Install | `Bash` | Clone repo, pip install, verify import |
| Init recon | `Agent(subagent_type="Explore")` | Scan repo for ML framework, key files |
| Interview | `AskUserQuestion` | One question per round with clickable options |
| Stage selection | `AskUserQuestion` (multiSelect) | Choose pipeline stages |
| Init confirmation | `AskUserQuestion` | Approve/edit research_program.md |
| Mode selection | `AskUserQuestion` | Choose single/hybrid/multi-agent |
| Quality gates | `AskUserQuestion` | User approval at gate stages |
| Code analysis | `Read`, `Grep`, `Glob` | Analyze target files |
| Code modification | `Edit` | Modify target files |
| Researchclaw calls | `Bash` | Delegate to researchclaw modules |
| Running experiments | `Bash` | Execute training/eval commands |
| Metric extraction | `Bash` | Extract metrics from logs |
| Results logging | `Edit` or `Bash` | Append to results.tsv |
| Checkpoint | `Write` | Save checkpoint.json after each stage |
| Lessons | `Write` | Save lesson JSON files |
| Analysis | `Agent(subagent_type="data-scientist", run_in_background=true)` | Periodic trend analysis |
| Literature | `Bash` (researchclaw) or `WebSearch` | Search for relevant papers |

## Key Principles

- **Deep-interview gates the research** — Thoroughly understand the project before experimenting.
- **Single measurable metric** — The core requirement. No metric = no auto_research.
- **ML domain knowledge matters** — Not just random changes, but informed experiments.
- **Guard before accept** — Tests must pass. Never keep broken code.
- **Git as checkpoint** — Every experiment is a commit.
- **Bounded by default** — 10 iterations unless overridden. Prevents runaway loops.
- **PIVOT/REFINE/PROCEED** — Structured decision logic. Max 2 pivots, 2 refines.
- **Quality gates** — Automated + human checkpoints at configurable stages.
- **Self-learning** — Extract lessons from failures, load in future iterations.
- **Graceful degradation** — Full pipeline with researchclaw, ML-aware loop without it.
- **Checkpoint and resume** — Never lose progress.
- **Stage selection** — User controls which stages run. All 23 ON by default.
- **Categorize experiments** — Track what types of changes work for this project.
- **Adaptive strategy** — Shift from exploration to exploitation based on results.
- **Simplicity criterion** — Complexity cost weighed against improvement magnitude.
- **Never stop** — Autonomous loop runs until interrupted (when unlimited).
- **research_program.md is portable** — Can be used with any AI agent.
- **.auto_research/ is ephemeral** — Gitignored, project-local, disposable.
