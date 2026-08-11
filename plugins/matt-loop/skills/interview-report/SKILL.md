---
name: interview-report
description: Turns a completed grilling interview log (question → decision → rationale triples) into a single self-contained, Notion-style light-theme HTML file anyone can skim and understand. Called by matt-auto right after its interview stage finishes — do not trigger this standalone on a bare grill-me/grill-with-docs session; matt-auto is what pulls it in.
---

# Interview Report

Turn the interview log matt-auto's delegate produced — every question it faced during `$grill-with-docs`/`$grill-me`, its decision, and the one-line rationale — into something a person can actually read in under a minute.

## Why this exists

The raw log is a flat transcript, complete but not *readable*: a real interview can run to dozens of questions, and nobody wants to scroll a wall of Q&A to find out what actually got decided. This turns the transcript into something skimmable — a plain-language summary up top, detail underneath organized so a reader only opens what they want to go deeper on.

## When this runs

Only as part of matt-auto's pipeline, right after its interview stage (step 4) concludes — in both its default and `--yolo` modes, since both run the interview, just routed to the delegate either way. Don't run this off a standalone `$grill-me`/`$grill-with-docs` session; those aren't matt-auto's concern and this report is specifically about what the delegate decided on the user's behalf.

## Input

The interview log matt-auto accumulated: an ordered list of `{question, decision, rationale}`, plus which of those (if any) were escalated to the real user instead of answered by the delegate.

## Output

One self-contained HTML file — no external fonts, scripts, or CDNs, so it opens correctly offline — written to `docs/agents/interview-reports/<slug>.html` (create the directory if it doesn't exist). Use the same `<slug>` matt-auto is already using for its own `--yolo` decision log, if it's running in that mode; otherwise a short kebab-case name for the idea under discussion.

Report the saved path back to the user in your final message — a file nobody's told about might as well not exist.

## Structure

Copy `assets/template.html` and fill in the content — it already has the light Notion-style look (background, typography, toggle blocks via native `<details>/<summary>`, callout boxes) worked out. Don't redesign the CSS from scratch each run; that's the whole point of bundling it.

1. **Title** — the idea/feature name, one line.
2. **Plain-language summary** — 2–4 sentences, no jargon, answering "what got decided and why" for someone with zero context on the codebase or the interview. This is the only part a skimming reader has to read.
3. **The decisions**:
   - **5 or fewer questions** — list them flat (template's Case A). Grouping a short list just adds clicks for nothing.
   - **More than 5** — group into named topic sections (template's Case B), one `<details>` toggle per topic. Name sections from what the interview actually covered ("Scope", "Data model", "Error handling", whatever came up) — don't force a fixed taxonomy onto an interview that didn't have one.
4. **Escalated decisions**, if any — call these out in their own section with the template's `.escalated` callout, since these are the ones the real user answered directly and are worth being able to spot at a glance. Omit the section entirely if nothing was escalated.

## Writing the summary and section labels

Write for someone who has zero context on the interview — a teammate skimming this a week later, or the user's manager. Every "what got decided" line should stand on its own without requiring the reader to already know the question that prompted it: translate ("we decided X because Y"), don't just relabel the raw question.

## Red flags

- Dumping the raw Q&A log into the template unedited → the point is translation into plain language, not reformatting.
- Grouping a 4-question interview into topic sections → adds friction for no benefit; use the flat list.
- Redesigning the CSS instead of using the template → inconsistent output between runs is the failure mode this skill exists to prevent.
- Running this outside matt-auto, off a bare grilling session → out of scope; the report is specifically about delegate decisions.
