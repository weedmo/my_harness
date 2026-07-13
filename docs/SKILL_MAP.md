# Skill & Framework Routing Guide

A decision aid for picking the right approach per task. Built from the installed
harness (weed-harness + superpowers + ouroboros + understand-anything + codex)
and the native Workflow tool.

> **Golden rule:** Ceremony scales to the task. Three *independent* inputs decide
> the approach — never collapse them into one axis.

---

## 0. The three independent inputs

| Input | Question | Decides |
| :-- | :-- | :-- |
| **Clarity** | Are the requirements unambiguous? | How much **interview / human gating** |
| **Scale** | How big, and do the parts run in parallel? | Which **execution engine** |
| **Risk** | How costly is a wrong direction / a bad change? | How deep the **verification gates** |

These are orthogonal. A task can be *clear + large + high-risk* (skip interview,
fan out with a workflow, but add adversarial verification gates).

---

## 1. TL;DR decision flow

```
[1] Requirements clear?
      ├─ NO  → clarify first: brainstorming / grill-me / grill-spec
      │         (resolve ambiguity, THEN re-evaluate)
      └─ YES → skip heavy interview; machine consensus (ralplan / Codex) is enough

[2] Now pick the EXECUTION ENGINE by scale:
      trivial (typo, 1-liner, obvious fix) → just do it directly (NO skill)
      small / sequential                   → single skill: tdd (mattpocock/superpowers) / diagnose
      large / sequential + review matters   → subagent-driven-development (superpowers)
                                              or team (OMC)
      large / parallel / audit / migration  → Workflow tool (ultracode)
      single goal, run until done           → ralph (ouroboros)

[3] Apply RISK modifier (independent of clarity):
      high risk → add gates even when clear:
                  grill-spec → verify-plan / refine-plan → then execute
```

---

## 2. Decision matrix

| Clarity | Risk | Scale | Recommended path |
| :-- | :-- | :-- | :-- |
| Vague | — | — | **Interview first** (grill-spec / brainstorming), then re-judge |
| Clear | Low | trivial / small | **Direct** or single skill (tdd (mattpocock/superpowers) / diagnose) |
| Clear | Low | large · parallel | **Workflow / ultracode** |
| Clear | Low | large · sequential | **OMC team** or **subagent-driven-development** (autonomous) |
| Clear | **High** | large | Autonomous + **verification gates** (grill-spec → verify-plan → execute) |

**Anti-pattern:** Running brainstorming's HARD-GATE or a workflow on a trivial fix.
That is over-engineering and contradicts "Simplicity First". superpowers is NOT
the "simple/auto" tier — it is ceremony-heavy.

---

## 3. The execution engines (same layer, different shapes)

All of these are *execution-layer* tools. They differ on **autonomy**,
**parallelism**, and **who drives the control flow**.

| Engine | Source | Flow driver | Parallel? | When |
| :-- | :-- | :-- | :-- | :-- |
| **Direct** | — | me | no | trivial / small |
| **subagent-driven-development** | superpowers | model (me) | sequential, review-gated | large sequential, review quality matters, same session |
| **executing-plans** | superpowers | model (me) | sequential, parallel session | large sequential, separate session |
| **Workflow / ultracode** | native tool | **code (JS script)** | **massively parallel** fan-out | large, independent units, audits, migrations |
| **ralph** | ouroboros | MCP loop | iterative (generations) | single goal, evolve until convergence |
| **team** | OMC | orchestrator | multi-agent team | large autonomous, clear spec |

**Loop vs Workflow:** a loop repeats over *time* (1 context, N iterations — ralph,
ultrawork). A workflow distributes over *space* (N agents, parallel — and may
*contain* loops). They are different axes, not synonyms.

**Goal vs engine:** a goal (goal-set → goal.md = testable exit criteria) is the
*destination*. It steers any engine (loop or workflow) and tells it when to stop.
Goal + workflow = the parallel engine gains a stopping condition and converges.

---

## 4. The three frameworks compared

| | **superpowers** | **OMC** (oh-my-claudecode) | **ouroboros** |
| :-- | :-- | :-- | :-- |
| Philosophy | design-first, human-gated | autonomous orchestration | spec-first + **evolutionary loop** |
| Interview | **heavy** (HARD-GATE) | light (machine consensus) | **heavy** (Socratic + ambiguity scoring) |
| Verification | human review | Codex consensus | **3-stage gate** (mechanical → semantic → multi-model) |
| Differentiator | design approval gates | parallel agent team | **evaluate → evolve** self-improvement, replayable contract |
| Loop | none (linear) | borrows ralph | **evolution loop is the core** |
| Install status | installed (6.0.3) | vendored into weed-harness (runtime in `.omx`) | installed (0.42.5), ralph lives here |

**Camp note:** superpowers and ouroboros are both *interview-heavy* (clarify
first). OMC is the *low-interview autonomous* camp. Picking by clarity:
vague → superpowers/ouroboros interview; clear → OMC autonomous.

---

## 5. Skill catalog by category

### Design / planning (front of the pipeline)
- **brainstorming** (superpowers) — idea → approved spec, HARD-GATE before any code
- **grill-me** (mattpocock) — relentless interview to stress-test a plan/design
- **grill-spec** (custom) — *adversarial verification* of an existing spec; writes
  resolutions back into the file, re-commits
- **writing-plans** (superpowers) — spec → multi-step implementation plan
- **to-prd** — synthesize conversation into a PRD, publish to tracker (no interview)
- **goal-set** — compress approved plan → goal.md (testable exit criteria)
- **verify-plan / refine-plan** — Codex↔Claude consensus to harden a plan in-place
- **ouroboros: interview / seed** — Socratic interview → immutable spec

### Execution
- **subagent-driven-development** (superpowers) — fresh impl agent + review per task
- **executing-plans** (superpowers) — same, in a parallel session
- **Workflow / ultracode** (native) — parallel agent fan-out, adversarial verify
- **ralph** (ouroboros) — evolutionary loop until convergence
- **team / team-dispatch** (OMC) — multi-agent team execution

### Debugging
- **diagnose** — 6-phase discipline; Phase 1 (build a fast deterministic
  pass/fail feedback loop) is 90% of the skill
- **investigate** (gstack) — 4-phase, "Iron Law: no fix without root cause"
- **systematic-debugging** (superpowers) — superpowers-integrated debugging

### Verification / quality
- **verification-before-completion** (superpowers) — evidence before claiming done
- **code-review** (`/code-review`, `ultra` for cloud multi-agent)
- **simplify** — reuse/simplification/efficiency cleanups (quality, not bugs)
- **receiving/requesting-code-review** (superpowers)

### Infrastructure
- **using-git-worktrees** (superpowers) — isolated workspace before feature work;
  prerequisite for parallel/subagent execution
- **worktree-spawn** — deterministic PORT_BASE for parallel multi-port dev servers

### Architecture / knowledge
- **improve-codebase-architecture** (mattpocock) — find deepening/refactor opportunities
- **graphify** (standalone, `~/.claude/skills/graphify` via `graphify install`) — any input → knowledge graph (code/docs/papers/images)
- **understand-anything** — codebase → interactive knowledge graph

---

## 6. The canonical pipeline (substantial work)

```
brainstorming / grill-me      ← clarify (if vague)
        ↓
grill-spec                    ← adversarial verify of the spec (if risky)
        ↓
writing-plans / to-prd        ← plan / PRD
        ↓
verify-plan / refine-plan     ← machine-harden the plan (Codex)  [risk gate]
        ↓
goal-set                      ← goal.md = exit criteria
        ↓
using-git-worktrees           ← isolated workspace
        ↓
EXECUTE  ── pick by scale ──→  subagent-driven / executing-plans / Workflow / ralph / team
        ↓
verification-before-completion + code-review
        ↓
finishing-a-development-branch
```

Not every task uses every stage. Trivial work skips the whole thing — just do it.

---

## 7. Quick anti-pattern checks

- Trivial fix → reaching for brainstorming/workflow = **over-engineering**
- Treating superpowers as the "simple/auto" tier = **backwards** (it is heavy)
- Picking "superpowers vs workflow" by clarity = **wrong axis** (clarity → interview;
  scale → engine)
- Running a workflow on tightly-coupled sequential tasks = **wasted parallelism**
  (use subagent-driven instead)
- Autonomous execution on a vague spec = **fast path to confidently-wrong output**
- `.omx` is OMC runtime state (logs/metrics/routing) — **not a skill**, keep it
  git-ignored
```
