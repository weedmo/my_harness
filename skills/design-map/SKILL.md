---
name: design-map
description: Visual-first design flow. Explore the codebase, present the design as a diagram Artifact (not prose), iterate until the user says the design is understood and settled, then write a local spec file and gate it with code-review. No GitHub issues are filed. Ends ready-to-implement. Trigger on /design-map, "구조 설계하자", "다이어그램으로 설계", or when the user wants to design a structure visually before implementing.
---

# design-map

Design through diagrams, not walls of text. The deliverable of every round is an
updated Artifact the user can look at; prose in chat stays to a few sentences.

Hard rules:
- Never file GitHub issues or use any external tracker. The spec is a local file.
- The user's explicit confirmation ("확정", "이해됐어", "이걸로 가자") is the only
  thing that moves the flow from design to spec. Do not self-declare the design done.
- One Artifact URL for the whole session — republish the same file, never fork a new one.
- All deliverables are written in Korean: the Artifact page (headings, labels,
  descriptions, decision tables) and the spec document. Identifiers that refer to
  real code — module/function/file names, diagram node names, commands — stay in
  English as they appear in the codebase.
- Never hand the user a link before the render check (step 3) has passed on the
  version that is live. A diagram with clipped, overflowing, or overlapping text is
  not a deliverable, even if the design behind it is right.

## Flow

### 1. Scope
Pin down what is being designed: which module/feature/system, and what problem the
new structure must solve. If ambiguous, ask once with AskUserQuestion (max one round),
then proceed.

### 2. Survey
Understand the current shape before proposing a new one. **graphify first** — it is
the standard way to read an existing codebase here; token-heavy file sweeps are the
last resort.
1. `graphify-out/graph.json` exists → use it: `graphify query "..." --budget N` for
   orientation, `--dfs` to trace paths. Refresh a stale graph with `graphify --update`.
2. No graph yet → build it: `graphify <repo> --directed --wiki`. If the CLI is
   missing, `pip install graphifyy` first.
3. graphify unavailable or the build fails → fall back: small scope, read the
   relevant files yourself; larger scope, send an Explore agent and keep the
   conclusions, not the file dumps.
The graph is for orientation (where is X, how is it connected). Verify precise
details (exact signatures, all callers) against the real source before drawing them.
Collect real names (modules, functions, tables) — diagrams built from real names,
never placeholders.

### 3. Diagram the design
Load the `artifact-diagramming` skill first, then build one Artifact page containing:
- **Current structure** — how it is wired today (only if something exists already).
- **Proposed structure** — the design. When a real fork in the road exists, show
  two alternatives side by side (design-it-twice) with a short tradeoff table and
  a recommendation; otherwise one proposal is fine.
- **Decision list** — each open question as a row: question / options / your pick / why.
Use mermaid or inline SVG per the diagramming skill's guidance.

Theme check (MANDATORY before every publish): the page must be legible in both
light and dark viewer themes. Define the complete palette as CSS tokens on bare
`:root` (light values), redefine only the tokens under
`@media (prefers-color-scheme: dark)` guarded as `:root:not([data-theme="light"])`,
and again under `:root[data-theme="dark"]`; give `body` an explicit token
background. Never let any color's only definition live inside one theme block,
and never hardcode text/stroke colors in diagrams (SVG included) that assume one
background — that is the dark-background-with-black-text bug. Scan the stylesheet
for this before publishing.

Make the page itself editable (load the `artifact-capabilities` skill first —
it is the authority; declare only what its roster serves):
- Declare `capabilities: {artifact: {}}` on the first publish.
- Decision-list cells and description blocks are editable in place: keep the
  design state as data embedded in the page, render from it, and on an explicit
  save action (a visible "저장" button, not on every keystroke) regenerate the
  full document from that state and call `artifact.publish(html)`. Never
  serialize the live DOM. `await claude.use("artifact")` can resolve `null` —
  then hide the editing affordances and the page stays a plain view.

Korean text is wide — size everything for it before drawing. Budget one
font-size per Hangul glyph (Latin needs about half). Inline SVG: put each box
and its label in one `<g>`, and make the rect at least
`chars × font-size + 24px` wide; a label that does not fit gets split across
lines or shortened, never squeezed. Mermaid: always quote labels
(`A["라벨"]`), keep them to roughly 12 Hangul characters, break longer ones
with `<br/>`, and move explanations to the caption — mermaid estimates CJK
width badly, which is exactly what produces clipped labels and nodes drawn on
top of each other.

Publish, then run the render check below. Only when it passes, hand the user
the link and tell them the three ways to respond: chat, selecting any part of
the page and commenting, or editing the text directly and pressing 저장.

Render check (MANDATORY after every publish that touches a diagram or layout):
the host lays the page out with its own fonts and mermaid version, so what the
local file looks like proves nothing — check the live page.
1. Open the published URL in a browser that carries the user's claude.ai login
   (the `claude-in-chrome` tools; new tab, never one the user is working in).
   Fallback when no logged-in browser is reachable: write a scratch copy of the
   file that adds `<script src="https://cdnjs.cloudflare.com/ajax/libs/mermaid/11.12.2/mermaid.min.js">`
   (mermaid fences only render natively on the host), serve the scratch
   directory with `python3 -m http.server <port>` and open the copy over
   `http://localhost` with the playwright or chrome-devtools tools (`file://`
   is blocked there). Say in the handoff that the check ran on a local render.
2. Run this in the page and read the result; anything but `OK` is a defect:
   ```js
   (() => {
     const out = [];
     const sel = ':scope > rect, :scope > path, :scope > polygon, :scope > circle, :scope > ellipse';
     const inside = (a, b) => a.left >= b.left - 1 && a.right <= b.right + 1 && a.top >= b.top - 1 && a.bottom <= b.bottom + 1;
     const hit = (a, b) => !(a.right <= b.left || b.right <= a.left || a.bottom <= b.top || b.bottom <= a.top);
     if (document.body.innerText.includes('\uFFFD')) out.push('garbled: U+FFFD in page text');
     document.querySelectorAll('body *').forEach(el => {
       if (getComputedStyle(el).overflow !== 'visible' && el.scrollWidth > el.clientWidth + 1)
         out.push('clipped: "' + (el.textContent || '').trim().slice(0, 30) + '"');
     });
     document.querySelectorAll('svg').forEach((svg, i) => {
       const shapeOf = g => [...g.querySelectorAll(sel)].map(s => s.getBoundingClientRect()).find(r => r.width > 2 && r.height > 2);
       const gs = [...svg.querySelectorAll('g')].filter(shapeOf);
       const leaves = gs.filter(g => !gs.some(o => o !== g && g.contains(o)));
       const boxes = [];
       leaves.forEach(g => {
         const s = shapeOf(g);
         const texts = [...g.querySelectorAll('text, foreignObject')];
         if (!texts.length) return;
         const label = texts[0].textContent.trim().slice(0, 20);
         boxes.push({ s, label });
         texts.forEach(t => {
           if (!inside((t.querySelector('span') || t).getBoundingClientRect(), s)) out.push(`overflow svg#${i}: "${label}"`);
         });
       });
       for (let a = 0; a < boxes.length; a++) for (let b = a + 1; b < boxes.length; b++) {
         const A = boxes[a].s, B = boxes[b].s;
         if (hit(A, B) && !inside(A, B) && !inside(B, A)) out.push(`overlap svg#${i}: "${boxes[a].label}" x "${boxes[b].label}"`);
       }
     });
     return out.length ? out.join('\n') : 'OK';
   })()
   ```
   It flags clipped HTML text, replacement characters, a label whose glyphs
   leave its box, and two labeled boxes that partially overlap (a box fully
   inside another — a mermaid subgraph around its nodes — is nesting, not a
   defect). Hand-drawn SVG is only checked where box and label share a `<g>`.
3. Take a full-page screenshot and look at it yourself — the script cannot see
   edge labels crossing nodes, arrows through text, or a diagram wider than the
   page. Then set `document.documentElement.dataset.theme = 'dark'` (and
   `'light'` if the browser is already dark), re-run the script, and screenshot
   again — the fonts do not change between themes, but contrast bugs do.
4. Any finding → fix the source file (shorten or wrap the label, widen the box,
   change the mermaid direction or split the diagram), republish to the same
   path, and run the check again. Repeat until it comes back `OK` in both
   themes. Report in one line what the check covered and which browser it ran in.

### 4. Understanding loop
Feedback arrives three ways; treat all of them as design input:
- **Chat** — as before.
- **Artifact comments** — the user selects part of the page and comments.
  Threads sent to Claude wake this session (the publish arms auto-replies);
  plain comments don't, so also check `Artifact(action: "comments")` when the
  user says they left notes. Apply the feedback to the diagram, reply briefly
  with what changed, and resolve the threads you handled.
- **In-page edits** — the user's 저장 publishes a new version. A republish
  notification means the local file is behind: re-read the live version
  (`action: "read"`), merge its state into your file, and build every later
  update on top of it. A publish conflict is the same signal — merge onto the
  handed-back version, never force.
Each round: apply feedback to the same Artifact (same file path → same URL),
run the render check from step 3 on the republished page, answer questions by
pointing at the diagram, keep decision-list rows updated.
Repeat until the user confirms the design is understood and settled. If they go
quiet mid-loop, the design is NOT confirmed — wait or ask, don't advance.

### 5. Spec
Before writing, re-read the live artifact (`action: "read"`) — the user may have
edited decisions in place since your last publish; the live version is the
source of truth. Then write the spec as a local markdown file (Korean prose,
English code identifiers), default
`docs/design/<topic>.md` in the repo (create the directory if needed; if the repo
has an existing spec/docs convention, follow it instead). Contents:
- Goal and non-goals
- The confirmed structure (embed the final mermaid diagram source)
- Decisions made, with one-line rationale each (from the decision list)
- Implementation order: a short numbered list of steps with a verify check per step
Do NOT publish it anywhere — no issues, no PRs.

### 6. Review gate
Run the `code-review` skill with the spec file as the path target (low effort).
If findings come back, fix the spec and update the Artifact to match. If the
code-review skill is unavailable in the session, spawn one general-purpose agent to
adversarially review the spec (contradictions, missing edge cases, steps that can't
be verified) and apply what survives.

### 7. Handoff
Report in chat: spec path, Artifact link, and the first implementation step.
Stop there — implementation starts only when the user asks. Offer to enter plan
mode or start step 1 on request.
