# Autocode v2 PGE Extension — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the `/autocode` SKILL.md with a PGE (Plan-Generate-Execute) team-based strategic loop that adds architecture redesign capabilities when experiments plateau.

**Architecture:** Single SKILL.md file modification. The skill is a markdown specification that Claude Code follows — no traditional code files. Changes add: extended HITL interview, dual-mode execution (single/pge), PGE agent roles, outer/inner loop flow, and state machine documentation. Existing single-agent mode is fully preserved.

**Tech Stack:** Markdown skill specification (SKILL.md), OMC state management (`.omc/state/`), Claude Code Agent API

**Spec:** `~/.claude/skills/autocode/docs/2026-04-16-autocode-pge-design.md`

---

### Task 1: Update Frontmatter, Overview, and Subcommands

**Files:**
- Modify: `~/.claude/skills/autocode/SKILL.md:1-28`

- [ ] **Step 1: Update frontmatter description to mention PGE**

Replace lines 1-5 with:

```markdown
---
name: autocode
description: "Autonomous code improvement loop with PGE (Plan-Generate-Execute) team mode. Single-agent mode: sequential experiments with PIVOT/REFINE logic. PGE mode: team-based experiments with retrospective-driven architecture redesign. Optional 23-stage research pipeline (AutoResearchClaw). Subcommands: install, init, run, status, resume."
argument-hint: "<subcommand: install|init|run|status|resume> [iterations]"
---
```

- [ ] **Step 2: Update overview section**

Replace lines 7-18 with:

```markdown
# Autocode — Autonomous Code Improvement

Autonomous experiment loop for code improvement with two execution modes:

- **Single mode**: One agent modifies code, measures metrics, keeps improvements, discards regressions.
  PIVOT/REFINE decision logic for strategy adjustment within a fixed architecture.
- **PGE mode**: Team of agents (Planner/Generator/Evaluator) runs experiments. On plateau,
  spawns Researcher and Architect to find new directions and redesign the architecture.
  Escapes local optima through retrospective-driven architecture evolution.

Both modes support bounded iterations, quality gates, self-learning from past failures,
and an optional 23-stage research pipeline via [AutoResearchClaw](https://github.com/aiming-lab/AutoResearchClaw).

Inspired by [autoresearch](https://github.com/karpathy/autoresearch) — same pattern, generalized beyond ML training.

> **For ML-specific research** (model training, hyperparameter tuning, architecture experiments), use `/auto_research` instead. It includes deep-interview initialization, ML domain knowledge, and experiment categorization.
```

- [ ] **Step 3: Update subcommands table**

Replace lines 20-28 with:

```markdown
## Subcommands

| Command | Action | User Confirmation |
|---------|--------|-------------------|
| `/autocode install` | Clone AutoResearchClaw + pip install | Not needed |
| `/autocode init [N]` | Extended HITL interview, generate `program.md`, select mode (single/pge). N = max iterations (default 10, 0 = unlimited) | Required |
| `/autocode run` | Execute based on mode in `program.md` (single or pge) | Not needed (autonomous) |
| `/autocode status` | Show progress, including architecture version and redesign history (pge) | Not needed |
| `/autocode resume` | Resume from checkpoint (supports both modes) | Not needed |
```

- [ ] **Step 4: Verify changes**

Read `~/.claude/skills/autocode/SKILL.md` lines 1-35 and confirm:
- Frontmatter mentions PGE
- Overview describes both modes
- Subcommands table includes mode selection in init

- [ ] **Step 5: Commit**

```bash
cd ~/.claude/skills/autocode && git add SKILL.md && git commit -m "feat(autocode): update frontmatter, overview, and subcommands for PGE mode"
```

---

### Task 2: Extend Step 2 (Init) with HITL Brainstorming Pattern

**Files:**
- Modify: `~/.claude/skills/autocode/SKILL.md:92-220`

This is the largest change. The existing Step 2 has sections 2A-2D. We replace 2B (gather info) with a brainstorming-pattern interview that collects both core and PGE fields, add 2E (mode selection), and update 2D (program.md schema).

- [ ] **Step 1: Replace Step 2B (Gather Information) with brainstorming-pattern interview**

Replace the existing Step 2B section (lines ~105-131) with:

```markdown
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
```

- [ ] **Step 2: Add Step 2E (Mode Selection) after existing 2D**

After the existing Step 2D (Generate program.md), add:

```markdown
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
```

- [ ] **Step 3: Update Step 2D (program.md schema) to unified format**

Replace the existing program.md template in Step 2D with the unified schema from the spec:

```markdown
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

- **execution_mode**: {single|pge}

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
```

- [ ] **Step 4: Verify changes**

Read `~/.claude/skills/autocode/SKILL.md` and confirm:
- Step 2B uses brainstorming pattern with one-question-at-a-time
- Required fields table includes all 10 fields
- Dynamic follow-up rules table is present
- Completion gate logic is documented
- Step 2D has unified program.md schema with Architecture and Plateau Detection sections
- Step 2E mode selection is present after 2D

- [ ] **Step 5: Commit**

```bash
cd ~/.claude/skills/autocode && git add SKILL.md && git commit -m "feat(autocode): extend init with HITL brainstorming pattern and mode selection"
```

---

### Task 3: Add PGE State Machine Section

**Files:**
- Modify: `~/.claude/skills/autocode/SKILL.md` — insert new section before Step 3

- [ ] **Step 1: Add PGE State Machine section between Step 2 and Step 3**

Insert after Step 2E and before Step 3:

```markdown
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

Write state after every phase transition:
```bash
# Example: transition from experiment to evaluate
Write autocode-pge-state.json with updated phase="evaluate"
```
```

- [ ] **Step 2: Verify changes**

Read the inserted section and confirm:
- State file JSON schema matches spec
- Phase transition diagram is present
- Plateau detection formula is present
- Hook integration notes are present

- [ ] **Step 3: Commit**

```bash
cd ~/.claude/skills/autocode && git add SKILL.md && git commit -m "feat(autocode): add PGE state machine section"
```

---

### Task 4: Add PGE Agent Roles Section

**Files:**
- Modify: `~/.claude/skills/autocode/SKILL.md` — insert after PGE State Machine, before Step 3

- [ ] **Step 1: Add PGE Agent Roles section**

Insert after the PGE State Machine section:

```markdown
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

#### Agent Spawning

All agents are spawned via `Agent()` tool. Core agents are spawned fresh each iteration (stateless — clean context window). On-demand agents are spawned in foreground (need results before continuing).

```
# Planner spawn example
Agent(
  description="Plan next autocode experiment",
  subagent_type="general-purpose",
  model="sonnet",
  prompt="Read architectures/v{N}.md and results.tsv. Write plans/plan_{iter}.md with the next experiment to try. Focus on {strategy_hints}."
)

# Researcher spawn example (on plateau)
Agent(
  description="Research optimization techniques",
  subagent_type="general-purpose",
  model="sonnet",
  prompt="Read retrospectives/retro_v{N}.md. The following directions are exhausted: {exhausted_list}. Search for new optimization techniques via web search and codebase patterns. Write research/research_{N}.md."
)
```

#### Communication

All inter-agent communication is file-based via `.autocode/` directory. No direct messaging between agents.
```

- [ ] **Step 2: Verify changes**

Read the section and confirm:
- Core agents table has 3 entries with correct models
- On-demand agents table has 2 entries
- Agent spawn examples are present
- File-based communication is stated

- [ ] **Step 3: Commit**

```bash
cd ~/.claude/skills/autocode && git add SKILL.md && git commit -m "feat(autocode): add PGE agent roles section"
```

---

### Task 5: Modify Step 3 (Run) with Mode Branching and PGE Flow

**Files:**
- Modify: `~/.claude/skills/autocode/SKILL.md:224-460`

This is the core change. Step 3 currently contains the single-agent experiment loop. We add a mode check at the top that branches to either the existing flow (single) or the new PGE flow.

- [ ] **Step 1: Add mode branching at the start of Step 3**

After the existing Step 3 heading and before 3A, insert:

```markdown
### Step 3: Run (`/autocode run`)

#### 3-Mode: Mode Detection

1. Read `$PROGRAM_FILE` to determine `execution_mode`.
2. If `execution_mode == "single"`: proceed to **3A (Single Mode)** below.
3. If `execution_mode == "pge"`: proceed to **3P (PGE Mode)** below.
```

- [ ] **Step 2: Wrap existing 3A-3M in a "Single Mode" section**

Rename the existing sections:
- `3A` → `3A` stays as-is but nested under a `#### Single Mode (3A-3M)` header
- Add a note at the top: "This is the existing single-agent experiment loop. No changes from v1."

Add before the existing 3A:

```markdown
#### Single Mode (3A-3M)

**Applies when `execution_mode=single`.** This is the original autocode experiment loop, unchanged from v1. PIVOT/REFINE/PROCEED logic handles plateau within a fixed architecture.
```

- [ ] **Step 3: Add PGE Mode section after Single Mode**

After the existing 3M (Loop Termination), add the entire PGE flow:

```markdown
---

#### PGE Mode (3P)

**Applies when `execution_mode=pge`.** Team-based experiment loop with retrospective-driven architecture redesign.

#### 3P-A: Pre-flight Checks

1. Verify `$PROGRAM_FILE` exists. If not: `program.md not found. Run /autocode init first.`
2. Read `$PROGRAM_FILE` to load configuration.
3. Verify target files exist.
4. Verify guard command passes on current code.
5. Load lessons from `$LESSONS_DIR/*.json` if any exist.
6. Create experiment branch: `git checkout -b autocode-pge/{date}` from current branch.
7. Read or create initial architecture: `$AUTOCODE_DIR/architectures/v1.md`.
8. Initialize PGE state file:

```json
Write to .omc/state/autocode-pge-state.json:
{
  "active": true,
  "mode": "pge",
  "session_id": "<current>",
  "outer_loop": { "architecture_version": 1, "redesign_count": 0 },
  "inner_loop": { "iteration": 0, "max_iterations": <from program.md>, "phase": "pge_init", "consecutive_discards": 0, "improvement_rate_window": [] },
  "plateau": { "detected": false, "trigger_reason": null, "researcher_pending": false, "architect_pending": false },
  "termination": { "reason": null, "target_metric": <from program.md or null>, "target_reached": false, "budget_exhausted": false },
  "best": { "metric": null, "commit": null, "architecture_version": 1 }
}
```

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
    Spawn Planner agent:
      Agent(
        description="Plan autocode experiment #{iteration}",
        model="sonnet",
        prompt="You are the Planner for an autocode PGE loop.
          Read: $AUTOCODE_DIR/architectures/v{arch_version}.md (current architecture)
          Read: $AUTOCODE_DIR/results.tsv (experiment history)
          Read: $AUTOCODE_DIR/lessons/ (past lessons)
          Write: $AUTOCODE_DIR/plans/plan_{iteration}.md
          Create a focused experiment plan: what to change, why, expected impact.
          Strategy: {strategy_hints from program.md}"
      )

    # 2. GENERATE
    Update state: phase="experiment"
    Spawn Generator agent:
      Agent(
        description="Execute autocode experiment #{iteration}",
        model="sonnet",
        prompt="You are the Generator for an autocode PGE loop.
          Read: $AUTOCODE_DIR/plans/plan_{iteration}.md
          Modify: {target_files from program.md}
          Steps:
            a. Read the plan and edit target files accordingly
            b. git add {target_files} && git commit -m 'experiment: {description}'
            c. Run guard: {guard_command}
               - If fails: attempt fix (max 2 tries). Still failing → revert, report crash.
            d. Run metric: {metric_command}
               - Redirect output to $AUTOCODE_DIR/logs/exp_{iteration}.log
            e. Report result: {metric_value, status, description}"
      )

    # 3. EVALUATE
    Update state: phase="evaluate"
    Spawn Evaluator agent:
      Agent(
        description="Evaluate autocode experiment #{iteration}",
        model="opus",
        prompt="You are the Evaluator for an autocode PGE loop.
          Read: $AUTOCODE_DIR/results.tsv (full history)
          Read: Generator's result for iteration #{iteration}
          Read: git diff of latest commit
          Tasks:
            a. Judge: keep (improved) / discard (equal or worse) / crash (guard failed)
               - keep: record in results.tsv, update best baseline
               - discard: git reset --hard HEAD~1, record in results.tsv
               - crash: git reset --hard HEAD~1, record in results.tsv
            b. Extract lesson → $AUTOCODE_DIR/lessons/lesson_{N}.json
            c. Plateau detection (compound trigger):
               plateau = (consecutive_discards >= 3 AND improvement_rate(last_5) < 0.5%)
                      OR (consecutive_discards >= 5)
            d. Report: {verdict, plateau_detected, plateau_reason}"
      )

    # 4. BRANCH
    if evaluator.plateau_detected:
        Update state: plateau.detected=true, plateau.trigger_reason=<reason>
        → Exit inner loop, enter Outer Loop (3P-D)
    elif iteration >= max_iterations and max_iterations > 0:
        Update state: termination.budget_exhausted=true, termination.reason="budget"
        → Terminate (3P-F)
    elif best.metric meets performance_target:
        Update state: termination.target_reached=true, termination.reason="target"
        → Terminate (3P-F)
    else:
        Reset consecutive_discards if this was a keep
        → Next iteration
```

#### 3P-D: Outer Loop (Strategic — on plateau)

Triggered when Evaluator detects plateau.

```
# 1. RETROSPECT
Update state: phase="retrospect"
Spawn Evaluator (retrospective mode):
  Agent(
    description="Autocode PGE retrospective for architecture v{N}",
    model="opus",
    prompt="You are the Evaluator in retrospective mode.
      Read: $AUTOCODE_DIR/results.tsv (full experiment history)
      Read: $AUTOCODE_DIR/architectures/v{N}.md (current architecture)
      Read: git log --oneline on autocode-pge/ branch
      Write: $AUTOCODE_DIR/retrospectives/retro_v{N}.md
      Analyze:
        - Metric trend over all iterations under this architecture
        - Which types of changes were effective vs ineffective
        - What optimization directions have been exhausted
        - What the plateau pattern suggests about remaining headroom
      Output a structured retrospective with:
        ## Metric Trend
        ## Effective Patterns
        ## Ineffective Patterns
        ## Exhausted Directions
        ## Remaining Opportunities (if any visible)"
  )

# 2. RESEARCH
Update state: phase="research", plateau.researcher_pending=true
Spawn Researcher agent:
  Agent(
    description="Research new optimization directions",
    model="sonnet",
    prompt="You are the Researcher for an autocode PGE loop.
      Read: $AUTOCODE_DIR/retrospectives/retro_v{N}.md
      Read: $AUTOCODE_DIR/architectures/v{N}.md
      The following directions are exhausted: {exhausted_directions from retro}
      Tasks:
        - Search the web for optimization techniques relevant to this codebase
        - Search the codebase for patterns similar to successful experiments
        - Look for unexplored optimization areas (data structures, algorithms, caching, etc.)
      Write: $AUTOCODE_DIR/research/research_{N}.md
      Structure:
        ## Techniques Found
        ## Codebase Patterns
        ## Recommended New Directions (ranked by expected impact)"
  )
Update state: plateau.researcher_pending=false

# 3. REDESIGN
Update state: phase="redesign", plateau.architect_pending=true
Spawn Architect agent:
  Agent(
    description="Redesign architecture for autocode PGE",
    model="opus",
    prompt="You are the Architect for an autocode PGE loop.
      Read: $AUTOCODE_DIR/retrospectives/retro_v{N}.md
      Read: $AUTOCODE_DIR/research/research_{N}.md
      Read: $AUTOCODE_DIR/results.tsv (full history)
      Read: $AUTOCODE_DIR/architectures/v{N}.md (current architecture)
      Read: program.md → forbidden_zones, immutable_constraints, scope
      Decision: Is an architecture change promising based on the research?
        YES → Write $AUTOCODE_DIR/architectures/v{N+1}.md with:
          ## Architecture Changes
          ## Rationale (linked to research findings)
          ## Expected Impact
          ## Migration Notes (what the Generator needs to know)
        NO → Keep current architecture. Update strategy hints only.
      Report: {redesigned: true/false, new_version: N+1 or N}"
  )
Update state: plateau.architect_pending=false

# 4. TRANSITION
if architect.redesigned:
    Update state: outer_loop.architecture_version += 1, outer_loop.redesign_count += 1
    Update state: plateau.detected=false, inner_loop.consecutive_discards=0
else:
    Update state: plateau.detected=false, inner_loop.consecutive_discards=0

→ Check termination (3P-E), then re-enter Inner Loop (3P-C)
```

#### 3P-E: Termination Check

After each outer loop cycle:

```
if inner_loop.iteration >= inner_loop.max_iterations and max_iterations > 0:
    → Terminate with reason="budget_exhausted"
elif best.metric meets performance_target:
    → Terminate with reason="target_reached"
else:
    → Re-enter Inner Loop (3P-C) with new architecture
```

#### 3P-F: Termination and Summary

```
Update state: active=false, inner_loop.phase="terminated"

Display:
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
| v3      | 36-50     | 112.7       | -22.4%      | added connection pooling |

### Top Improvements
1. {description} ({delta}%)
2. ...

### Retrospective Links
- retrospectives/retro_v1.md
- retrospectives/retro_v2.md
- research/research_1.md
- research/research_2.md
```
```

- [ ] **Step 4: Verify changes**

Read the entire Step 3 section and confirm:
- Mode detection at top branches to single or pge
- Single mode wraps existing 3A-3M unchanged
- PGE mode has sections 3P-A through 3P-F
- Inner loop: Planner → Generator → Evaluator → branch
- Outer loop: Retrospect → Research → Redesign → transition
- Termination check covers budget + target
- Final summary includes architecture evolution table

- [ ] **Step 5: Commit**

```bash
cd ~/.claude/skills/autocode && git add SKILL.md && git commit -m "feat(autocode): add PGE run mode with inner/outer loop and agent spawning"
```

---

### Task 6: Update Step 4 (Status) for PGE

**Files:**
- Modify: `~/.claude/skills/autocode/SKILL.md` — Step 4 section

- [ ] **Step 1: Extend status output for PGE mode**

After the existing status display, add a PGE-specific section:

```markdown
### Step 4: Status (`/autocode status`)

1. If `$RESULTS_FILE` doesn't exist: `No results yet. Run /autocode init then /autocode run.`

2. Read and parse `results.tsv`, `checkpoint.json`, and mode from `program.md`.

3. **If mode=single**, display existing summary (unchanged from v1):

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

4. **If mode=pge**, display PGE summary:

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

### Recent Experiments
| # | Iter | Commit | Metric | Status | Description | Delta |
|---|------|--------|--------|--------|-------------|-------|
...
```

5. If experiments are currently running, also show time elapsed and experiments per hour.
```

- [ ] **Step 2: Verify changes**

Read Step 4 and confirm mode branching in status output.

- [ ] **Step 3: Commit**

```bash
cd ~/.claude/skills/autocode && git add SKILL.md && git commit -m "feat(autocode): update status command for PGE mode"
```

---

### Task 7: Update Step 5 (Resume) for PGE

**Files:**
- Modify: `~/.claude/skills/autocode/SKILL.md` — Step 5 section

- [ ] **Step 1: Extend resume for PGE mode**

Replace the existing Step 5 with:

```markdown
### Step 5: Resume (`/autocode resume`)

1. Verify `$PROGRAM_FILE`, `$RESULTS_FILE`, and `$CHECKPOINT_FILE` exist.
   If not: `No checkpoint found. Run /autocode init then /autocode run first.`
2. Read mode from `program.md`.

**If mode=single:**

3. Read checkpoint to restore state: iteration, stage, pivot/refine counts, best metric.
4. Load lessons from `$LESSONS_DIR`.
5. Detect the experiment branch and verify it's checked out.
6. Read execution mode from `$AUTOCODE_DIR/mode.txt` (default: `single` if missing).
7. Display:
   ```
   Resuming autocode (single mode):
   - Branch: autocode/{date}
   - Iteration: {current}/{max_iterations}
   - Stage: {stage_name} ({stage_id})
   - Current best: {autocode_metric_name}: {value}
   - Resuming pipeline...
   ```
8. Continue the pipeline loop (3A-3M) from the checkpointed stage and iteration.

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
7. Continue the PGE loop (3P-C or 3P-D) from the checkpointed phase:
   - If phase is `experiment` or `plan`: re-enter Inner Loop (3P-C) at current iteration
   - If phase is `retrospect`, `research`, or `redesign`: re-enter Outer Loop (3P-D) at that phase
   - If phase is `terminated`: report final summary and exit
```

- [ ] **Step 2: Verify changes**

Read Step 5 and confirm both single and pge resume paths are documented.

- [ ] **Step 3: Commit**

```bash
cd ~/.claude/skills/autocode && git add SKILL.md && git commit -m "feat(autocode): update resume command for PGE mode"
```

---

### Task 8: Update File Structure, Tool Usage, and Key Principles

**Files:**
- Modify: `~/.claude/skills/autocode/SKILL.md` — bottom sections

- [ ] **Step 1: Update file structure documentation**

Replace the existing `.autocode/` structure references with the unified file structure:

```markdown
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
│   ├── v1.md                     # initial architecture
│   ├── v2.md                     # 1st redesign
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
```

- [ ] **Step 2: Update tool usage table**

Add PGE-specific tool usage entries to the existing table:

```markdown
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
```

- [ ] **Step 3: Update key principles**

Add PGE-specific principles to the existing list:

```markdown
## Key Principles

- **Single measurable metric** — the core requirement. No metric = no autocode.
- **Guard before accept** — tests/lint must pass. Never keep broken code.
- **Git as checkpoint** — every experiment is a commit. Easy to review, revert, cherry-pick.
- **Simplicity criterion** — complexity cost must be weighed against improvement magnitude.
- **Bounded by default** — 10 iterations unless overridden. Prevents runaway loops.
- **Adaptive strategy** — shift from systematic exploration to focused exploitation based on results.
- **PIVOT/REFINE/PROCEED** — (single mode) structured decision logic prevents thrashing.
- **Quality gates** — automated + human checkpoints at configurable stages.
- **Self-learning** — extract lessons from failures, load them in future iterations.
- **Graceful degradation** — full pipeline with researchclaw, basic loop without it.
- **Checkpoint and resume** — never lose progress. Resume from any interruption point.
- **Stage selection** — user controls which pipeline stages run.
- **Redirect output** — never let experiment output flood the context window.
- **Validate metrics** — always check that extracted metrics are finite numbers.
- **program.md is portable** — can be used with any AI agent, not just Claude Code.
- **results.tsv is the log** — untracked by git, append-only record of all experiments.
- **.autocode/ is ephemeral** — gitignored, project-local, disposable.
- **PGE: Architecture evolution** — plateau triggers architecture redesign, not just parameter tweaking.
- **PGE: Stateless agents** — fresh context window per agent spawn prevents context pollution.
- **PGE: File-based communication** — agents communicate via `.autocode/` files, not messages.
- **PGE: Compound plateau detection** — multiple signals (consecutive discards + improvement rate) prevent false triggers.
- **PGE: Versioned architectures** — every redesign is a new document. Compare, rollback, learn.
- **PGE: Single budget** — `max_iterations` is the only hard limit. Time and redesign count are unlimited.
- **PGE: Hook persistence** — boulder pattern via `.omc/state/autocode-pge-state.json` ensures loop survives compaction.
```

- [ ] **Step 4: Verify all changes**

Read the full SKILL.md and confirm:
- File structure section includes PGE directories
- Tool usage table has PGE agent entries
- Key principles include PGE-specific items
- No broken markdown formatting
- No orphaned references to removed sections

- [ ] **Step 5: Commit**

```bash
cd ~/.claude/skills/autocode && git add SKILL.md && git commit -m "feat(autocode): update file structure, tool usage, and key principles for PGE"
```

---

## Self-Review Checklist

**Spec coverage:**
- [x] Extended HITL interview with brainstorming pattern → Task 2
- [x] Dual-mode execution (single/pge) → Task 1 (overview), Task 2 (mode selection), Task 5 (run branching)
- [x] PGE state machine → Task 3
- [x] PGE agent roles → Task 4
- [x] Inner loop (experiments) → Task 5 (3P-C)
- [x] Outer loop (retrospect → research → redesign) → Task 5 (3P-D)
- [x] Plateau detection (compound trigger) → Task 3 (state machine), Task 5 (evaluator logic)
- [x] Termination conditions (budget + target) → Task 5 (3P-E, 3P-F)
- [x] Versioned architecture documents → Task 4 (architect role), Task 5 (outer loop)
- [x] Updated status for PGE → Task 6
- [x] Updated resume for PGE → Task 7
- [x] File structure with PGE directories → Task 8
- [x] Hook integration (boulder pattern) → Task 3

**Placeholder scan:** No TBD, TODO, or "implement later" found.

**Type consistency:**
- `autocode-pge-state.json` field names consistent across Tasks 3, 5, 7
- Agent model assignments consistent: Planner=sonnet, Generator=sonnet, Evaluator=opus, Researcher=sonnet, Architect=opus
- File paths consistent: `architectures/v{N}.md`, `plans/plan_{iter}.md`, `retrospectives/retro_v{N}.md`, `research/research_{N}.md`
- Phase names consistent: `pge_init`, `plan`, `experiment`, `evaluate`, `retrospect`, `research`, `redesign`, `terminated`
