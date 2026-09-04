---
name: loop-report
description: "Builds and delivers the live progress page of a long-running delegated loop (matt-auto, autocode, and any loop that runs for minutes to hours on the user's behalf) — one self-contained HTML the user can read while the loop runs and keep afterwards. Owns delivery end to end — an Orca artifact link (`orca artifacts share`/`update`), or the worktree's Orca built-in browser tab when links are unavailable, with the route kept stable for the whole run — and owns the build (`assets/render.py` over `assets/shell.html` plus the calling loop's view). Callers say probe / publish and relay the answer; they never run `orca artifacts`, `tab`, or `reload` themselves. Called by interview-report (matt-auto's decision graph) and autocode (the experiment board); do not trigger standalone."
---

# Loop report (the shared progress page)

A delegated loop runs unattended for a long time. Two things make that bearable for the person who delegated it: they can see where it is without opening a terminal, and the page they are looking at is the one that keeps updating. This skill owns both — the page and how it reaches the user — for every loop in this harness, so matt-auto and autocode do not each grow their own copy.

The loop owns its *graph* (what runs, in what shape: matt-auto's decision stages and ticket waves, autocode's hypothesis frontier and metric trend). This skill owns everything around it: the design system, the 진행 상황 header with percent, elapsed time and ETA, blockers, the 결과 panel measured from git, the auto-refresh poll, the theme toggle, the modal, and the delivery.

## When this runs

Only as part of a loop skill's run — the caller tells you which of two verbs it wants:

- **probe** — once, early, before the loop's first gate: which route this device can offer, so the user learns *before* the gate that there will be no link.
- **publish** — at the gate, then on every regeneration: build the page from the loop's data and push it wherever the user is already reading it. Answer with the route, the URL or tab, the path, and a one-line reason when the route is not `link`.

## Build

The caller writes its data as JSON next to the page and names its view. Render with the script that ships next to this file:

```
python3 <this skill's dir>/assets/render.py \
  --data <dir>/<slug>.data.json \
  --out  <dir>/<slug>.html \
  --view <the loop's skill dir>/assets/view.html
```

`<this skill's dir>` is the directory holding this SKILL.md — `~/.codex/skills/loop-report` on Codex when installed by the npx installer, the installed weed-harness plugin's `skills/loop-report` on Claude Code or a native Codex plugin install, `~/.agents/skills/loop-report` under Orca. That is the whole build. The script validates the common data contract below, then the view's own contract when a `validate.py` sits next to the view, and refuses to write a page that would render wrong — so a regeneration is "edit the JSON, rerun the script", nothing else. **Never splice the shell or a view by hand** — no `cp` + `sed`/`perl`/regex over them. The shell is 40 KB of CSS and JS full of `#`, `<script>`, and comments that repeat the data-block tag; a hand-rolled substitution silently ate 30 KB of it in testing and the page opened broken. If `python3` is missing, say so and stop — do not improvise a replacement.

Do not touch the shell's CSS or JavaScript, or a view's. The rendering machinery lives there, and consistent output between runs is the point of bundling it. The palette follows robodata's design tokens on Claude's warm dark base, with a light counterpart behind the 라이트/다크 toggle; both are restated token by token, never filtered. Don't add a third palette or hard-code a color outside the token blocks.

### Common data contract

```json
{
  "title": "실행 제목, in Korean",
  "slug": "run-slug",
  "generated": "2026-09-04",
  "summary": "2-4 plain-language sentences for someone with zero context, in Korean.",
  "progress": {
    "state": "running",
    "updated": "2026-09-04T10:12:00+09:00",
    "startedAt": "2026-09-04T09:30:00+09:00",
    "current": "지금 무엇을 하고 있는지 한 줄",
    "note": "선택 — 읽는 사람이 알아야 할 한 줄",
    "blockers": [ { "title": "H004", "reason": "측정 실패", "detail": "bench.py exit 2 — 머지 후 metric이 실행되지 않음" } ]
  },
  "outcome": {
    "baseRef": "2dacebe", "headRef": "3b0523e", "branch": "feature/x",
    "note": "이 diff가 무엇인지 한 줄 — 생략 가능",
    "files": [ { "path": "src/foo.ts", "status": "added", "kind": "code", "added": 120, "removed": 0, "note": "이 파일이 하는 일, 한 줄" } ]
  }
}
```

- Everything else in the file belongs to the view (see the loop's own skill for its keys).
- `progress` is present from the moment the loop is under way until it ends. `state` is `running` / `blocked` / `done`; `updated` is the ISO timestamp of this regeneration, read from the clock (`date -Iseconds`) at the moment you write the file — never rounded or typed from memory; the page shows "N분 전 갱신" from it and a future stamp makes that line lie. `startedAt` drives 경과. Percent and ETA come from the view (only it knows what a unit of work is); the shell renders them.
- **`progress.blockers`** is the shell's own blocker list — anything that stops the run right now that the view has no node for. `title` names the thing, `reason` is a short label, and `detail` is the specific, checkable fact. "막혔습니다" with no detail is the failure the box exists to prevent. A view may add its own blockers (matt-auto derives them from blocked tickets).
- **The page polls while `state` is not `done`** — it reloads itself every 30 s to pick up a republished version, skipping the reload whenever the reader has unsaved edits, with a toggle to stop it. A page with no `progress` yet (a gate) polls too, so a reader who leaves it open sees the run start. That is why `state: "done"` on the final regeneration matters: it is what stops the polling. Inside Orca's built-in browser the poll is inert — see Route 2; there you push each regeneration with `orca reload --page`.
- **`outcome` — the shipped-changes panel, final regeneration only.** Omit the key until the loop has finished and verified its work; then fill it together with `progress.state: "done"` (`render.py` refuses an `outcome` without it). The page renders it as *결과 — 이번 실행이 바꾼 것*: file counts by status, `+`/`−` totals split into 코드 / 문서 / 기타, and a per-file table. `status` is `added` / `modified` / `deleted` / `renamed`; `kind` is `code` / `docs` / `other` — docs covers `.md`/`.mdx`/`.txt`/`.rst` and anything under a docs directory, other covers lockfiles, generated output, and binary assets, code is the rest. `added` / `removed` are line counts **measured from git** (`git diff --numstat <baseRef>..<headRef>`) — never estimated, never eyeballed; a binary file gets `0`/`0` and a `note` saying so. Leave the loop's own bookkeeping (its log folder, `.unlazy/**`, `.autocode/**`) out of the tally. `note` is one Korean line per file and is what makes the table worth reading; a bare path list is the degraded form. Totals are computed in the page, so never pass pre-summed numbers. A view may add its own result tiles above the file table (autocode's metric summary).
- Write every human-facing string in Korean — `title`, `summary`, `current`, notes; ids and the JSON structure stay English.

### The view interface (for loop authors)

A view is one file, `assets/view.html` in the loop's skill, holding one `<style>` block and one `<script>` block, each tag at column 0. The script assigns `window.LoopView` with any of: `kind` (the page kind, shown in the title and meta line), `meta(data, ctx)`, `progress(data, ctx) → { percent, remainingMin, count } | null`, `blockers(data, ctx)`, `renderProgress(host, ctx)` (inside the 진행 상황 card), `renderOutcome(host, ctx)` (inside 결과, above the file table), `render(host, ctx)` (the main area), `hasUnsavedEdits()`. `ctx` carries the data and the shell's helpers (`el`, `bar`, `stat`, `section`, `kvRow`, `modal`, `clickable`, time formatters, `prefs`/`setPref`). A `validate.py` next to the view exposes `validate(data) → [errors]` and runs before every build. The shell's CSS classes (`.flow`, `.wcol`, `.tnode`, `.badge`, `.stat`, `.panel`, `.kv`, …) are the component set; a view adds only what the shell lacks. Read `assets/shell.html`'s header comment and the existing views (`interview-report`, `autocode`) before writing a new one.

## Delivery — this skill owns it

The file on disk is the source of truth; the route is how the user actually reads it. The caller never touches the transport — it says probe or publish and relays the answer, and every `orca artifacts` / `tab` / `reload` command in a run is issued from here.

Routes, in order of preference — take the first that works, then **stay on it for the whole run**:

1. **Orca artifact link** — the public URL; a gate hands the user this, not a path.
2. **Orca built-in browser tab** — the file opened in the worktree's browser pane inside the Orca desktop; works against a headless remote runtime.
3. **Path only** — when there is no Orca at all.

Keep the route in `<dir>/<slug>.delivery.json` next to the page — `{ "route": "link" | "tab" | "path", "bin": "orca" | "orca-ide", "url": …, "browserPageId": …, "denied": "artifact_sharing_disabled" | null }` — and read it before every publish. That is what makes a regeneration from a fresh subagent context land on the same link or the same tab instead of minting a second one. It is run bookkeeping, left out of the outcome tally like the rest of the log folder.

**Probe:** run `<orca> status --json` and `<orca> artifacts list --json`: both fine → `link`; `authentication_required` → `tab` (profile signed out — say so); no CLI or no runtime → `path`. `artifact_sharing_disabled` cannot be probed — it only shows on `share` — so a `link` answer is provisional until the first publish.

Pick the executable once, at the probe, and record it in the delivery file (`"bin"`): inside an Orca-managed terminal `orca` is the Orca CLI shim; in any other shell **on Linux use `orca-ide`** — bare `orca` there is usually the GNOME screen reader and running it starts speech on the user's machine. **If the shim fails with `bad option: --no-sandbox`** (unprivileged user namespaces disabled on that kernel — seen on Linux servers), that is a broken shim, not a missing Orca: fall back to `orca-ide`, which is on `PATH` on those hosts and talks to the same runtime. Only when neither binary works is Orca unavailable. Never let a shim error alone push the run to Route 3. The bundled `orca-cli` skill (`$orca-cli`, or `orca skills get orca-cli`) is the authority on every command below; this file only says how the report uses them. Never substitute another host, a screenshot, or a hand-rolled upload.

### Route 1 — Orca artifact link

- **First publish for this slug:** `<orca> artifacts share <dir>/<slug>.html --json` → the share URL comes back as `result.shareUrl` (without `--json` the URL is the whole stdout).
- **Every regeneration afterwards:** `<orca> artifacts update <the same path> --json`. Orca looks the artifact up by the resolved local path in the active profile, so the same path from the same profile keeps the same link — the user goes on reading the URL they already have. Only if `update` reports no such record (the file was never shared from this profile) fall back to `share`.
- The HTML must stay self-contained — Orca does not upload relative assets — which the shell already guarantees. The CLI transport caps a file at 800 KB; shell plus view plus a normal run's data sits far under it, so a size failure means the data block grew wrong.
- **Refused?** Write the file anyway, record why, and drop to Route 2 for this run:
  - `artifact_sharing_disabled` → publishing is off for the whole device and **only a human can turn it on**; there is no CLI or RPC way to grant it, so do not retry. Tell the user once: open Settings → Artifacts in the Orca desktop app on this device, turn on "Allow publishing public artifact links", and say the word — re-run `share` only when they have said so, never on every regeneration; when it then succeeds, switch the route to `link` and hand over the URL. On a headless runtime (`orca serve` on a server, paired from a desktop elsewhere) that switch may simply not be reachable, so the tab is the delivery for that run rather than something to wait for.
  - No Orca CLI on `PATH`, runtime unreachable, or `authentication_required` (profile signed out) → `Orca artifact unavailable: <why>`, then Route 2 (Route 3 when there is no runtime to open a tab in).

### What the hosted page can and cannot do

Orca serves the file inside a sandboxed iframe (`allow-downloads allow-forms allow-modals allow-popups allow-scripts`, no `allow-same-origin`) under an Orca chrome header. Verified against a live artifact:

- **Scripts run**, so the page renders, polls, and any view-level editing and export work — a blob download is covered by `allow-downloads`.
- **`localStorage` throws `SecurityError`** (the frame has an opaque origin). The shell and the views wrap every access in `try`/`catch`, so nothing breaks — but anything a view keeps in storage (matt-auto's edits) lives only for that page load. Say so when handing over a link to a page with edits: **export before reloading**, or edit the local file instead. Never "fix" this by removing the guards.
- The header shows the **original file name as the page title** (`<slug>.html`) and the artifact's expiry — links last 30 days, and each `update` restarts that window.

### Route 2 — Orca built-in browser tab

A path alone is not a deliverable — on a remote runtime the user cannot double-click it. Open the file in the worktree's Orca browser tab, which the desktop shows even when the runtime is a headless `orca serve` on another machine (verified against a remote runtime):

- **Once per run:** from inside the worktree, `<orca> tab create --url file://<absolute path> --json` → store `result.browserPageId` in the delivery file. Before creating one, `<orca> tab list --json` — if a tab already shows that `file://` URL, reuse its `browserPageId` instead of opening a second.
- **After every regeneration:** `<orca> reload --page <browserPageId> --json`. This is not optional: the built-in browser ignores every script-initiated reload or navigation of a `file://` page (`location.reload()`, `location.href = …`, `history.go(0)` — none of them fire, verified), so the page's own 30 s poll does nothing there and the rewritten file shows up only when you push it. `tab list` tells you if the tab is gone (`browser_tab_not_found`, or the URL no longer listed) — then create it again and update the delivery file.
- The page works normally inside that tab: `localStorage` is available, the theme toggle works, exports download.

### Route 3 — path only

Only when there is no Orca at all — no CLI, no runtime — is the local path the whole deliverable; say so, and expect the user to open the file in a browser of their own, where the page's own poll does work.

Report the route back in your final message — URL, or tab plus path, and the one-line reason when it is not a link. A file nobody's told about might as well not exist.

## Red flags

- Building the page with `cp` + `sed`/`perl` instead of `assets/render.py` → the shell is full of the characters those substitutions trip on; the script exists because that shortcut shipped a broken page.
- Editing the shell's or a view's CSS/JS instead of only the data → inconsistent, possibly broken output between runs is the failure mode this skill exists to prevent.
- A `progress.updated` typed from memory or in the future → the "N분 전 갱신" line lies.
- Leaving `state` at `running` on the final regeneration → the page polls forever and the run looks unfinished.
- Line counts in `outcome` that were estimated, read off a subagent's report, or summed by hand → they must come from `git diff --numstat`, and a wrong number in a results panel is worse than no panel.
- A blocker whose `detail` is vague ("실패함", "확인 필요") → the reader must be able to act on it without opening a terminal.
- Running `artifacts share` on a regeneration instead of `artifacts update` → the link the user already has is no longer the one you regenerated.
- Publishing anywhere but Orca's own artifacts (another host, a pasted screenshot, a hand-rolled upload) → Orca artifacts are the delivery mechanism; when they are unavailable the fallback is Orca's built-in browser tab on the local file, not a substitute service.
- Publishing without reading `<slug>.delivery.json` first → a second link or a second tab, and the user is now looking at the wrong one.
- Letting the caller run `orca artifacts` / `tab` / `reload` itself → two owners of one route drift apart; the caller says publish, this skill does it.
- Handing over a bare path when there is no link, while an Orca runtime is reachable → open the file in the worktree's browser tab; a path on a remote server is not something the user can click.
- Regenerating the file into an open Orca tab without `orca reload --page` → the tab keeps showing the old version; the page cannot reload itself there.
- Retrying a share denied with `artifact_sharing_disabled` on every regeneration → the answer cannot change until a human flips the device setting; re-run only when the user says they did.
- Calling bare `orca` from a non-Orca Linux shell → that is the GNOME screen reader; use `orca-ide`.
- Skipping the page, or leaving a gate without a deliverable, because publishing failed → the local HTML is still the report; only the link is missing, and the reason belongs in one line.
