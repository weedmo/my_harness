---
name: interview-report
description: "Renders matt-auto's decision log (question → decision → rationale, per pipeline stage) into the run's live decision-graph page — the pipeline stages in order, each decision as an editable node the user can rewrite or flag and export as <slug>.edits.json for matt-auto to rework from, plus the ticket waves, review and PR lanes while the run executes. The page itself is built and delivered by the shared `$loop-report` skill (weed-harness): this skill owns the decision-graph view and its data, writes `<slug>.data.json`, and hands it to loop-report to render and publish (artifact link, or the Orca browser tab when links are unavailable). matt-auto only says probe / publish and relays the answer. Called by matt-auto right after its interview stage and again before its final report — do not trigger this standalone on a bare grill-me/grill-with-docs session; matt-auto is what pulls it in."
---

# Interview Report (decision graph)

Turn the decision log matt-auto's delegate produced — every question it faced, its decision, and the one-line rationale, stage by stage — into an interactive graph a person can read in under a minute and *push back on* by editing it.

## Why this exists

The raw log is a flat transcript, complete but not *readable*: a real run answers dozens of questions across interview, seam check, ticket breakdown, and implementation, and nobody wants to scroll a wall of Q&A to find out what got decided where. The graph shows the pipeline as it actually ran — which stage came in what order, and which decisions and policies applied inside each stage — and because the user opted out of live confirms, the graph is also their steering wheel: any node they disagree with, they edit or flag right in the page and export the change for matt-auto to act on.

## When this runs

Only as part of matt-auto's pipeline:

1. Right after the interview stage (step 4) concludes — the graph then covers the interview decisions and marks later stages pending. This run feeds matt-auto's interview gate, so the published page is what the user is asked to approve; get it published before matt-auto presents the gate.
2. On every board update once tickets exist (the live board), and again before matt-auto's final report (and after the small path's `$implement`, and after ship mode's step 10) — regenerate the same file over the full decision log so the finished graph covers every stage, the last time **with the `outcome` block** so the page opens on what the run actually shipped.

Don't run this off a standalone `$grill-me`/`$grill-with-docs` session; this report is specifically about what the delegate decided on the user's behalf.

## Input

The decision log matt-auto accumulated: an ordered list of `{question, decision, rationale}` per pipeline stage, which of those were escalated to the real user, and each stage's current status (done / in progress / pending / skipped, with why). Once the run executes, also the ticket DAG, the wave plan, each ticket's state, and the review / PR state.

## Output

`docs/agents/matt-auto-log/<slug>.data.json`, next to the decision log, using the same `<slug>` — and from it, `docs/agents/matt-auto-log/<slug>.html`, one self-contained page. Regeneration rewrites both; the page keeps user edits safe across regenerations via `localStorage`, keyed by slug, where storage exists (see loop-report's hosted-page notes).

## How to build and deliver it

This skill owns the *view* — the decision graph, the wave flow, the ticket modal, the review and PR lanes, the edits round-trip — as `assets/view.html` and its data checks in `assets/validate.py`. The page around it and the delivery belong to **`$loop-report`** (weed-harness). So:

1. Write the data JSON (format below) to `docs/agents/matt-auto-log/<slug>.data.json`.
2. Hand it to `$loop-report` with this view — probe or publish, exactly as matt-auto asked:

   ```
   python3 <loop-report's dir>/assets/render.py \
     --data docs/agents/matt-auto-log/<slug>.data.json \
     --out  docs/agents/matt-auto-log/<slug>.html \
     --view <this skill's dir>/assets/view.html
   ```

   `<this skill's dir>` is the directory holding this SKILL.md; `<loop-report's dir>` is wherever weed-harness installed it (`~/.codex/skills/loop-report` under the npx installer on Codex, the weed-harness plugin's `skills/loop-report` under a native install, `~/.agents/skills/loop-report` under Orca). loop-report validates (common keys, then `validate.py`: stage keys, unique decision ids, ticket statuses and blockers, wave modes and `why`, `outcome` only with `review`), renders, and publishes on the run's route, keeping `<slug>.delivery.json` beside the page. Read its answer — link, tab, or path, with the reason — back to matt-auto verbatim.

Never splice a template by hand, never edit the shell or the view's CSS/JS, never run `orca artifacts` / `tab` / `reload` from here — those rules and the reasons are loop-report's. If `$loop-report` is not installed, say `loop-report unavailable — weed-harness 3.x required` once; the decision log on disk is then the only report, and matt-auto's board must say so.

### Data format

The common keys (`title`, `slug`, `generated`, `summary`, `progress`, `outcome`) follow loop-report's contract. The view's own keys:

```json
{
  "stages": [
    {
      "id": "interview",
      "name": "인터뷰",
      "skill": "grill-with-docs",
      "status": "done",
      "note": "",
      "decisions": [
        {
          "id": "interview-1",
          "question": "The question, restated plainly",
          "before": "The policy or de-facto behavior that held before, or null when none existed",
          "change": "new",
          "decision": "The decision (the after-state)",
          "rationale": "One-line rationale",
          "escalated": false
        }
      ]
    }
  ]
}
```

- `stages` appear in the order the pipeline ran them; the page draws the rail and connectors from that order. Use matt-auto's own stages (Interview, Size branch, Spec, Tickets, Confirm, Implement, Ship) and drop stages that never applied rather than listing empty shells — except skipped stages, which stay visible with `"status": "skipped"` and a `note` saying why (`"small path"`, `"autonomous"`).
- `status` is one of `done` / `in-progress` / `pending` / `skipped`. A stage may carry an explicit `percent`; otherwise done is 100, pending is 0, and an in-progress implement stage follows its tickets.
- Decision `id`s must be stable across regenerations (stage prefix + ordinal is fine) — `localStorage` edits and `edits.json` both key on them.
- `escalated: true` marks decisions the real user answered directly; the page highlights them.
- **`before` / `change` — the before → after view on every decision.** A decision is a move against what already held, and the node shows that move as two cells: `before` is the prior state — a documented policy, or the de-facto behavior the code already exhibited — or `null` when nothing existed (the page then reads *"없음 — 정해진 바 없었음"*). `change` classifies the move and shows as a badge even while the node is collapsed: `"new"` (신규 — nothing existed), `"redirect"` (방향 전환 — a prior direction existed and this changes it), `"keep"` (유지 — a prior policy was examined and confirmed). `decision` is always the after-state. Fill these whenever the log knows the before-state; a decision without `change` falls back to a plain single-line node, which is the degraded form, not a choice.
- **`progress` + `tickets` — the live board, present from the ticket stage until the run ends.** Together they render *진행 상황* above everything else: the run-wide percentage, elapsed and remaining time first, then the execution flow — **waves as columns left to right, each ticket a node inside its wave** — and a red blocker box for anything stuck. The decision graph moves below it behind a 결정 검토 disclosure (open by default at the interview gate, collapsed once a run is under way, and the reader's own choice sticks across the live reload). Omit both on the interview-gate generation (no tickets exist yet). A small-path run has no `tickets` or `plan`, but it still carries `progress` — `state` and `current` while `$implement` runs, `state: "done"` on the final regeneration — so the header says where the run is and the review lane has somewhere to render.

```json
"tickets": [
  { "id": "T3", "title": "결과 패널 렌더링", "status": "blocked",
    "blockedBy": [], "gates": { "met": 3, "total": 5 },
    "route": "matt-deep",
    "worker": { "model": "opus", "effort": "high",
                "dispatchId": "dispatch-7f2", "worktree": "matt-auto/T3" },
    "estimateMin": 25,
    "blocker": { "reason": "gate", "detail": "G4 스냅샷 테스트 실패 — 기대 +504/−175, 수신 +504/−134" },
    "note": "선택 — 막히지 않았을 때의 한 줄" }
]
```

  - Ticket `status` is `done` / `in-progress` / `blocked` / `pending` / `skipped`. `blockedBy` lists the ticket ids it waits on — that is the DAG edge, not a blocker.
  - **`blocker` is required on every `blocked` ticket** and is what the whole panel exists for: `reason` is one of `gate` / `escalation` / `ci` / `conflict` / `dependency` / `worker` / `review` / `other`, and `detail` is the specific, checkable fact — the unmet gate id and its expected-vs-actual, the failing check, the question awaiting an answer. "막혔습니다" with no detail is the failure this panel was built to prevent.
  - `gates` is the unlazy ledger tally when unlazy is installed (see `$loop-gates`); omit it otherwise.
  - **Who is doing the work shows on the node**: `route` is the routed agent, and `worker` carries the model and effort that route resolved to plus, for an Orca worker, its `dispatchId` and `worktree`. Fill both — "어떤 티켓을 어떤 서브에이전트가 어떤 모델로" is the question the node answers, and a node with only a route name half-answers it.

- **`plan` — how the run intends to execute the tickets.** Rendered as an ordered wave graph, so the reader sees which tickets run at once, which wait, and why. Fill it as soon as matt-auto has planned execution (right after the ticket DAG), and keep it through the run — the waves stay put while the tickets inside them change status.

```json
"plan": {
  "concurrency": 2,
  "placement": "local",
  "note": "선택 — 계획 전체에 대한 한 줄",
  "waves": [
    { "id": "W1", "mode": "parallel", "why": "서로 다른 파일만 건드려 충돌 위험이 없다",
      "tickets": ["T1", "T2"] },
    { "id": "W2", "mode": "sequential", "why": "같은 섹션을 고쳐 순차로 둔다",
      "tickets": ["T5"] }
  ]
}
```

  - `mode` is `parallel` or `sequential`; `why` is one Korean line saying what made it so — the file overlap, the risk, the dependency. A wave without `why` is a shape with no reasoning, which is what this panel exists to show; `validate.py` refuses it.
  - `concurrency` is how many workers may run at once; `placement` names where they run (`local`, or the environment name).
  - The page lays the waves out **left to right** and prints each wave's own duration (a parallel wave's slowest ticket, a sequential wave's sum). With no `plan` at all it still draws the flow, deriving one column per blocking level from `blockedBy` — so the shape survives a run that never planned waves.
- **Estimates and progress bars.** `progress.startedAt` (ISO) drives 경과; each ticket's `estimateMin` (and `startedAt` once it begins, `actualMin` once done) drives the rest. The page computes, and never asks you to pre-compute: the overall percent (estimate-weighted, an in-progress ticket counted by elapsed/estimate and capped at 90%), 남은 예상, and 완료 예정 시각 — a parallel wave costing its slowest ticket, a sequential one their sum. **`estimateMin` is the run's own guess and the page labels it 예상** — never present it as measurement, and never back-fill it to make a bar look better.
- **Ticket detail — what the modal shows.** A node is a summary; clicking it opens the ticket. Put the specifics here rather than in the node: `acceptance` (the ticket's criteria, as written), `steps` (what happened inside the ticket — 티켓 읽기 → `$implement` → 게이트 재검증 → 머지백, each `{ name, status, note }`), `gateList` (`{ id, text, status: met|unmet|manual, check, expect, actual }` — the `CHECK:` command and the expected-vs-actual are what make an unmet gate actionable), `files` and `commits`. Everything is optional; the modal renders the sections that exist.
- **`review` and `pr` — the tail of the flow.** The run does not end at the last ticket, so the flow does not either: `review` renders a 리뷰 lane (one node per review dimension, with its finding count) and `pr` renders a PR lane (number, `branch → base`, check rows, babysit cycles, link) at the right end of the same left-to-right flow.

```json
"review": { "status": "in-progress", "skill": "code-review", "note": "…",
  "passes": [ { "id": "r1", "name": "정확성", "status": "done", "findings": 2, "note": "…" } ] },
"pr": { "number": 128, "url": "https://…", "base": "dev", "branch": "matt-auto/x",
  "status": "in-progress", "cycles": 2, "note": "…",
  "checks": [ { "name": "CI", "status": "failed", "detail": "unit: 2 failing" },
              { "name": "리뷰어", "status": "pending", "detail": "변경 요청 1건" },
              { "name": "머지 가능", "status": "ok", "detail": "충돌 없음" } ] }
```

  - Check `status` is `ok` / `done` / `failed` / `pending`, and `detail` carries the measured fact, never a guess. Omit `pr` entirely on a run that opens no PR — the lane simply does not appear.
- **Long runs stay readable.** Once there are more than three waves, finished ones collapse to stubs and the flow scrolls itself to the wave that is actually running; a 완료 웨이브 펼치기 button brings the history back, and each stub expands on its own. Nothing needs doing in the data for this — but it is why a long plan is fine to publish in full.
- **`outcome`** follows loop-report's contract (files measured from `git diff --numstat` against matt-auto's baseline, bookkeeping under `docs/agents/matt-auto-log/**` and `.unlazy/**` left out). Fill it on the last regeneration only, together with `progress.state: "done"` **and the `review` block** — matt-auto always runs its review pass, small path included, and `validate.py` refuses an `outcome` without it.

### Writing the summary and decision text

**Always write the graph's content in Korean** — `title`, `summary`, stage `name`s and `note`s, and every `question`/`decision`/`rationale`. The page's own UI labels are already Korean; ids and the JSON structure stay English.

Write for someone who has zero context on the run — a teammate skimming this a week later. Every `question`/`decision` pair must stand on its own: translate ("X를 하기로 했다, 왜냐하면 Y"), don't paste the raw transcript line.

## The edits round-trip

The page lets the user rewrite a decision, flag a node as a problem with a comment, and click **수정 내보내기**, which downloads `<slug>.edits.json` (and copies it to the clipboard). The page tells them to save it into `docs/agents/matt-auto-log/`. matt-auto checks for that file at every invocation and treats each entry as a change request — that consumption logic is matt-auto's (see its Decision-graph report section), not this skill's. This skill's only obligations are stable decision ids and not breaking the view's export format. On the hosted artifact link `localStorage` is unavailable, so edits live only for that page load — say "export before reloading" when handing over a link; in the Orca tab they persist.

## Red flags

- Dumping the raw Q&A log into the JSON unedited → the point is translation into plain language, not reformatting.
- Writing the graph's content in English → the user reads this in Korean; only ids and JSON structure stay English.
- Building or publishing the page here instead of through `$loop-report` — hand-splicing, editing `view.html`'s CSS/JS, running `orca artifacts` / `tab` / `reload` → one owner for the page and its route; this skill owns the data and the view.
- Changing decision ids on regeneration → orphans the user's saved edits and any exported edits.json.
- Shipping `outcome` on the interview-gate generation → nothing has been built yet; the panel would be a lie.
- A `blocked` ticket whose `blocker.detail` is vague ("실패함", "확인 필요") → the reader must be able to act on it without opening a terminal.
- Leaving `state` at `running` on the final regeneration, or a `progress.updated` typed from memory → the page polls forever, or its "N분 전 갱신" line lies.
- A wave whose `why` is missing, or estimates invented to make the bar move → both turn the plan panel into decoration.
- Writing the file anywhere but `docs/agents/matt-auto-log/<slug>.html` → matt-auto and the edits round-trip both assume that path.
- Running this outside matt-auto, off a bare grilling session → out of scope; the report is specifically about delegate decisions.
