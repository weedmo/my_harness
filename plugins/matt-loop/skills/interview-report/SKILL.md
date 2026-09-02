---
name: interview-report
description: Renders matt-auto's decision log (question → decision → rationale, per pipeline stage) into a single self-contained interactive decision-graph HTML — the pipeline stages in order, each decision as an editable node the user can rewrite or flag and export as <slug>.edits.json for matt-auto to rework from, published as an Orca artifact link (`orca artifacts share`/`update`) so the user reads it in a browser instead of opening a local file. Called by matt-auto right after its interview stage and again before its final report — do not trigger this standalone on a bare grill-me/grill-with-docs session; matt-auto is what pulls it in.
---

# Interview Report (decision graph)

Turn the decision log matt-auto's delegate produced — every question it faced, its decision, and the one-line rationale, stage by stage — into an interactive graph a person can read in under a minute and *push back on* by editing it.

## Why this exists

The raw log is a flat transcript, complete but not *readable*: a real run answers dozens of questions across interview, seam check, ticket breakdown, and implementation, and nobody wants to scroll a wall of Q&A to find out what got decided where. The graph shows the pipeline as it actually ran — which stage came in what order, and which decisions and policies applied inside each stage — and because the user opted out of live confirms, the graph is also their steering wheel: any node they disagree with, they edit or flag right in the page and export the change for matt-auto to act on.

## When this runs

Only as part of matt-auto's pipeline:

1. Right after the interview stage (step 4) concludes — the graph then covers the interview decisions and marks later stages pending. This run feeds matt-auto's interview gate, so the published link is what the user is asked to approve; get it published before matt-auto presents the gate.
2. Again before matt-auto's final report (and after the small path's `$implement`, and after ship mode's step 10) — regenerate the same file over the full decision log so the finished graph covers every stage, this time **with the `outcome` block** so the page opens on what the run actually shipped.

Don't run this off a standalone `$grill-me`/`$grill-with-docs` session; this report is specifically about what the delegate decided on the user's behalf.

## Input

The decision log matt-auto accumulated: an ordered list of `{question, decision, rationale}` per pipeline stage, which of those were escalated to the real user, and each stage's current status (done / in progress / pending / skipped, with why).

## Output

One self-contained HTML file — no external fonts, scripts, or CDNs, so it opens correctly offline — written to `docs/agents/matt-auto-log/<slug>.html`, next to the decision log, using the same `<slug>`. Regeneration overwrites the same file; the page keeps user edits safe across regenerations via `localStorage`, keyed by slug.

Then publish it as an Orca artifact (below) and report both the link and the path.

## Publish it as an Orca artifact

The file on disk is the source of truth; the link is how the user actually reads it — matt-auto's interview gate hands them this URL, not a path they have to open by hand. Use Orca's own artifact mechanism, nothing else: the bundled `orca-cli` skill's **Artifacts** section is the authority (`$orca-cli`, or `orca skills get orca-cli`), and this section only says how matt-auto uses it. Never substitute another host, a screenshot, or a hand-rolled upload.

Pick the executable the way `orca-cli` does, once: inside an Orca-managed terminal `orca` is always the Orca CLI; in any other shell **on Linux use `orca-ide`** — bare `orca` there is usually the GNOME screen reader and running it starts speech on the user's machine.

- **First publish for this slug:** `<orca> artifacts share docs/agents/matt-auto-log/<slug>.html --json` → the share URL comes back as `result.shareUrl` (without `--json` the URL is the whole stdout).
- **Every regeneration afterwards:** `<orca> artifacts update <the same path> --json`. Orca looks the artifact up by the resolved local path in the active profile, so the same path from the same profile keeps the same link — the user goes on reading the URL they already have. Only if `update` reports no such record (the file was never shared from this profile) fall back to `share`.
- The HTML must stay self-contained — Orca does not upload relative assets — which the template already guarantees. The CLI transport caps a file at 800 KB; template plus a normal decision log sits far under it, so a size failure means the data block grew wrong.

### What the hosted page can and cannot do

Orca serves the file inside a sandboxed iframe (`allow-downloads allow-forms allow-modals allow-popups allow-scripts`, no `allow-same-origin`) under an Orca chrome header. Verified against a live artifact, this means:

- **Scripts run**, so the graph renders, edits, flags, and **Export edits** all work — the export's blob download is covered by `allow-downloads`.
- **`localStorage` throws `SecurityError`** (the frame has an opaque origin). The template already wraps every access in `try`/`catch`, so nothing breaks — but edits live only for that page load. Say so when handing over the link: **export before reloading**, or edit the local file instead. Never "fix" this by removing the guards.
- The header shows the **original file name as the page title** (`<slug>.html`) and the artifact's expiry — links last 30 days, and each `update` restarts that window.

Publishing can be refused, and that never cancels the report — write the file anyway and say in one line why there is no link:

- Code `artifact_sharing_disabled` → publishing is off for the whole device and **only a human can turn it on**; there is no CLI or RPC way to grant it, so do not retry. Tell the user to open Settings → Artifacts in the Orca desktop app on this device, turn on "Allow publishing public artifact links", and say the word — then re-run the share and hand them the link. Give them the local path meanwhile.
- No Orca CLI on `PATH`, runtime unreachable, or profile signed out → report `Orca artifact unavailable: <why>` plus the local path.

Report the share URL and the saved path back in your final message — a file nobody's told about might as well not exist.

## How to build it

Copy `assets/template.html` and fill in **only** the data:

- the `<title>` tag, and
- the JSON inside `<script id="graph-data" type="application/json">`.

Do not touch the CSS or the JavaScript — the rendering, editing, flagging, and export machinery lives there, and consistent output between runs is the point of bundling it. The palette is Orca's own artifact design language (its share page's tokens: `--background #0a0a0a`, `--card #171717`, `--muted-foreground #a1a1a1`, `--radius 0.625rem`, Geist/SF Mono stacks), so the report reads as part of Orca inside the artifact chrome rather than a page pasted into it. Never restyle per run.

### Data format

```json
{
  "title": "Feature name",
  "slug": "feature-slug",
  "generated": "2026-09-01",
  "summary": "2-4 plain-language sentences: what got decided and why, for someone with zero context.",
  "stages": [
    {
      "id": "interview",
      "name": "Interview",
      "skill": "grill-with-docs",
      "status": "done",
      "note": "",
      "decisions": [
        {
          "id": "interview-1",
          "question": "The question, restated plainly",
          "decision": "The decision",
          "rationale": "One-line rationale",
          "escalated": false
        }
      ]
    }
  ]
}
```

- `stages` appear in the order the pipeline ran them; the page draws the rail and connectors from that order. Use matt-auto's own stages (Interview, Size branch, Spec, Tickets, Confirm, Implement, Ship) and drop stages that never applied rather than listing empty shells — except skipped stages, which stay visible with `"status": "skipped"` and a `note` saying why (`"small path"`, `"autonomous"`).
- `status` is one of `done` / `in-progress` / `pending` / `skipped`.
- Decision `id`s must be stable across regenerations (stage prefix + ordinal is fine) — `localStorage` edits and `edits.json` both key on them.
- `escalated: true` marks decisions the real user answered directly; the page highlights them.
- **`outcome` — the shipped-changes panel, final regeneration only.** Omit the key entirely on the interview-gate run (nothing is built yet); fill it on the last regeneration, once implementation and review are done. The page renders it under the summary as *결과 — 이번 실행이 바꾼 것*: file counts by status, `+`/`−` totals split into 코드 / 문서 / 기타, and a per-file table. Totals are computed in the page from `files`, so never pass pre-summed numbers.

```json
"outcome": {
  "baseRef": "2dacebe",
  "headRef": "3b0523e",
  "branch": "matt-auto/feature-slug",
  "note": "이 diff가 무엇인지 한 줄 — 생략 가능",
  "files": [
    { "path": "src/foo.ts", "status": "added", "kind": "code",
      "added": 120, "removed": 0, "note": "이 파일이 하는 일, 한 줄" }
  ]
}
```

  - `status` is `added` / `modified` / `deleted` / `renamed`; `kind` is `code` / `docs` / `other` — docs covers `.md`/`.mdx`/`.txt`/`.rst` and anything under a docs directory, other covers lockfiles, generated output, and binary assets, code is the rest.
  - `added` / `removed` are line counts **measured from git** (`git diff --numstat <baseRef>..<headRef>`) — never estimated, never eyeballed. A binary file gets `0`/`0` and a `note` saying so.
  - Leave out the run's own bookkeeping — `docs/agents/matt-auto-log/**` and `.unlazy/**` — so the panel counts the work, not the reporting about it.
  - `path` is repo-relative; `note` is one Korean line per file and is what makes the table worth reading — a bare path list is the degraded form.

### Writing the summary and decision text

**Always write the graph's content in Korean** — `title`, `summary`, stage `name`s and `note`s, and every `question`/`decision`/`rationale`. The template's own UI labels are already Korean; ids and the JSON structure stay English.

Write for someone who has zero context on the run — a teammate skimming this a week later. Every `question`/`decision` pair must stand on its own: translate ("X를 하기로 했다, 왜냐하면 Y"), don't paste the raw transcript line.

## The edits round-trip

The page lets the user rewrite a decision, flag a node as a problem with a comment, and click **Export edits**, which downloads `<slug>.edits.json` (and copies it to the clipboard). The page tells them to save it into `docs/agents/matt-auto-log/`. matt-auto checks for that file at every invocation and treats each entry as a change request — that consumption logic is matt-auto's (see its Decision-graph report section), not this skill's. This skill's only obligations are stable decision ids and not breaking the template's export format.

## Red flags

- Dumping the raw Q&A log into the JSON unedited → the point is translation into plain language, not reformatting.
- Writing the graph's content in English → the user reads this in Korean; only ids and JSON structure stay English.
- Editing the template's CSS/JS instead of only the data block → inconsistent, possibly broken output between runs is the failure mode this skill exists to prevent.
- Changing decision ids on regeneration → orphans the user's saved edits and any exported edits.json.
- Line counts in `outcome` that were estimated, read off a subagent's report, or summed by hand → they must come from `git diff --numstat`, and a wrong number in a results panel is worse than no panel.
- Shipping `outcome` on the interview-gate generation → nothing has been built yet; the panel would be a lie.
- Running `artifacts share` on a regeneration instead of `artifacts update` → the link the user already has is no longer the one you regenerated.
- Publishing the graph anywhere but Orca's own artifacts (another host, a pasted screenshot, a hand-rolled upload) → Orca artifacts are the delivery mechanism; when they are unavailable the fallback is the local path, not a substitute service.
- Retrying a share denied with `artifact_sharing_disabled` → the answer cannot change until a human flips the device setting.
- Calling bare `orca` from a non-Orca Linux shell → that is the GNOME screen reader; use `orca-ide`.
- Skipping the report, or leaving the gate without a deliverable, because publishing failed → the local HTML is still the report; only the link is missing, and the reason belongs in one line.
- Writing the file anywhere but `docs/agents/matt-auto-log/<slug>.html` → matt-auto and the edits round-trip both assume that path.
- Running this outside matt-auto, off a bare grilling session → out of scope; the report is specifically about delegate decisions.
