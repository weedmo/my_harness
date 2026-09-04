# Diet inventory — interview-report SKILL.md (before: 2,661 words)

| # | Item (rule / step / red flag) | Before (line) | After (where it lives now) |
|---|---|---|---|
| 1 | Purpose: decision log → readable interactive graph the user can push back on | 6-8 | L8-11 |
| 2 | Why: flat log unreadable; graph is the steering wheel (edit/flag/export) | 10-12 | L8-11 (one clause) |
| 3 | When (a): right after interview stage; feeds interview gate; publish before gate presented | 18 | L17-18 |
| 4 | When (b): every board update once tickets exist; before final report (after small-path $implement, after ship step 10); last with `outcome` | 19 | L19-21 |
| 5 | Not standalone off grill-me/grill-with-docs | 21, 161 | L23-24, red flag L221 |
| 6 | Input: decision log per stage, escalations, stage status; later ticket DAG, waves, ticket state, review/PR | 25 | L28-30 |
| 7 | Output paths: `docs/agents/matt-auto-log/<slug>.data.json` + `<slug>.html`; regeneration rewrites both | 29 | L34-35 |
| 8 | Skill owns view.html + validate.py; page shell + delivery are loop-report's | 33 | L39-40 |
| 9 | Build step: write data → render.py with --view this skill's assets/view.html; loop-report validates (list of checks) | 35-45 | L42-56 (render.py + deliver.py publish; validate list L53-55) |
| 10 | <this skill's dir> / <loop-report's dir> location hints | 45 | L53 (pointer to loop-report's SKILL.md instead of repeating the three paths) |
| 11 | Relay delivery answer to matt-auto verbatim | 45 | L58-59 |
| 12 | One owner: never hand-splice / edit shell or view CSS-JS / run orca commands here | 47 | L58 (one sentence: deliver.py's alone; no hand-splice / CSS-JS edits) |
| 13 | loop-report missing → say `loop-report unavailable — weed-harness 3.x required` once; log on disk is the report; matt-auto board says so | 47 | L59-61 |
| 14 | Data format: common keys per loop-report contract; stages JSON example | 51-76 | L65-89 |
| 15 | stages in pipeline order; matt-auto stage names; drop never-applied stages, keep skipped with note | 78 | L91-94 |
| 16 | stage status enum; optional percent, defaults | 79 | L95-96 |
| 17 | decision ids stable across regenerations | 80 | L97 |
| 18 | escalated: true highlighted | 81 | L98 |
| 19 | before/change: before = prior state or null (없음 text); change new/redirect/keep badge; decision = after; fill when known; missing change = degraded | 82 | L101-107 |
| 20 | progress + tickets live board: renders 진행 상황 (percent, elapsed/remaining, waves as columns, blocker box); graph below in 결정 검토 disclosure (open at gate, collapsed under way, sticks); omit both at interview gate; small path: no tickets/plan but progress with state/current then done | 83 | L108-115 |
| 21 | tickets JSON example | 85-96 | L117-127 |
| 22 | ticket status enum; blockedBy = DAG edge not blocker | 98 | L129-130 |
| 23 | blocker required on blocked; reason enum; detail = checkable fact | 99 | L132-135 |
| 24 | gates = unlazy tally when installed; omit otherwise | 100 | L136 |
| 25 | route + worker (model, effort, dispatchId, worktree) both filled | 101 | L137-139 |
| 26 | plan: ordered wave graph; fill right after ticket DAG; keep through run | 103 | L141-142 |
| 27 | plan JSON example | 105-117 | L144-156 |
| 28 | wave mode enum; why one Korean line; validate.py refuses missing why | 119 | L158-159 |
| 29 | concurrency / placement meaning | 120 | L160 |
| 30 | waves left→right with duration; no plan → derived columns from blockedBy | 121 | L161-162 |
| 31 | estimates: progress.startedAt drives 경과; estimateMin/startedAt/actualMin; page computes percent (weighted, in-progress capped 90%), 남은 예상, 완료 예정; estimateMin labeled 예상, never measurement, never back-filled | 122 | L163-167 |
| 32 | ticket detail (modal): acceptance, steps {name,status,note}, gateList {id,text,status,check,expect,actual}, files, commits; all optional | 123 | L168-172 |
| 33 | review + pr lanes at the tail of the flow | 124 | L173-175 |
| 34 | review/pr JSON example | 126-134 | L177-185 |
| 35 | check status enum; detail measured not guessed; omit pr when no PR | 136 | L187-188 |
| 36 | long runs: page collapses finished waves; publish long plans in full | 137 | L189-190 |
| 37 | outcome: loop-report contract, exclusions; last regeneration only, with state done and review; validate refuses without review | 138 | L191-194 |
| 38 | Korean content rule; ids + structure English | 142 | L198-199 |
| 39 | Write for zero-context reader; translate, don't paste | 144 | L199-201 |
| 40 | Edits round-trip: 수정 내보내기 → <slug>.edits.json into docs/agents/matt-auto-log/; matt-auto consumes; obligations = stable ids + export format | 148 | L205-209 |
| 41 | Red flag: raw Q&A dump | 152 | L213 |
| 42 | Red flag: English content | 153 | L214 |
| 43 | Red flag: building/publishing here (hand-splice, CSS/JS, orca cmds) | 154 | folded into L58 (delivery is deliver.py's; never hand-splice / edit view CSS-JS) — not a separate red flag |
| 44 | Red flag: unstable ids | 155 | L215 |
| 45 | Red flag: outcome on the gate page | 156 | L216 |
| 46 | Red flag: vague blocker.detail | 157 | L217-218 |
| 47 | Red flag: state running / updated from memory on final page | 158 | L219-220 |
| 48 | Red flag: missing wave why / invented estimates | 159 | L221 |
| 49 | Red flag: wrong path | 160 | L222-223 |
| 50 | Red flag: standalone use | 161 | L224 |

After: 1,798 words (target ≤ 1,800). Description 84 words, mentions loop-report build+delivery.
