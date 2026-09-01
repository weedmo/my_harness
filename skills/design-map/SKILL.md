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

Publish and hand the user the link, telling them the three ways to respond:
chat, selecting any part of the page and commenting, or editing the text
directly and pressing 저장.

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
answer questions by pointing at the diagram, keep decision-list rows updated.
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
