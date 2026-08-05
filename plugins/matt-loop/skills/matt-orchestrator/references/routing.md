# Matt skill routing

Select the smallest useful set. A skill is a workflow, not a ceremonial role.

| Signal | Skill | Worker role | Parallel guidance |
| --- | --- | --- | --- |
| Flow is unclear | `$ask-matt` | Read-only router | Run alongside repository reconnaissance. |
| Broken, failing, throwing, or slow behavior | `$diagnosing-bugs` | Read-only diagnosis, then bounded fix owner | Parallelize competing hypotheses; serialize edits after evidence converges. |
| Feature or fix requested test-first | `$tdd` | Vertical-slice implementation owner | Keep red-green-refactor and its files with one worker. |
| PRD or requirement issues already define the work | `$implement` | Implementation owner | Explicit invocation is required. Partition by non-overlapping vertical slice. |
| Module seam or public interface needs design | `$codebase-design` | Read-only design advisor or interface owner | Complete the interface decision before dependent implementations. |
| Domain terms or invariants are changing | `$domain-modeling` | Model advisor or documentation owner | Run discovery in parallel; gate implementation on agreed terminology when public behavior changes. |
| External API or documented fact is uncertain | `$research` | Read-only evidence gatherer | Parallel-safe; require primary-source evidence and a report artifact. |
| A design question needs disposable evidence | `$prototype` | Isolated experiment | Keep prototype output outside production paths unless explicitly promoted. |
| Branch or work-in-progress needs review | `$code-review` | Standards-axis and Spec-axis review tasks | Run the two axes as separate review-only worker tasks after implementation. |
| User wants an interactive bug-reporting session | `$qa` | Issue-capture facilitator | Do not use as a default implementation verifier; it files durable GitHub issues. |
| Merge or rebase is already conflicted | `$resolving-merge-conflicts` | Single conflict-resolution owner | Do not parallelize edits to conflicted files. |
| Refactor plan must be filed as an issue | `$request-refactor-plan` | Planning and issue-authoring owner | Treat issue creation as external state and keep one owner. |

## Common DAGs

### Bug fix

`reproduction loop -> diagnosing-bugs hypotheses (parallel) -> cause/test-seam decision -> tdd fix -> Standards review + Spec review + repository checks (parallel)`

### Feature from requirements

`optional ask-matt when routing is unclear + codebase reconnaissance -> interface/domain decision -> independent implement or tdd slices (parallel) -> Standards review + Spec review (parallel) -> integration checks`

### Refactor

`codebase-design + behavior characterization (parallel) -> seam decision -> non-overlapping refactor slices -> Standards review + behavior verification`

Avoid parallel writes when tasks touch the same interface, registry, migration chain, snapshot set, lockfile, or generated artifact.
