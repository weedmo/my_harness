---
description: "Adversarial verification of a spec/design/plan doc using grill-me — stress-test holes, write resolutions back into the file, re-commit"
argument-hint: "[path/to/spec.md]  (optional — defaults to the most recent spec/plan)"
---

# Grill Spec — Adversarial Verification Pass

You are running an **adversarial verification** of an already-written spec/design/plan document.
This is the *review lane*, not the author lane. You did NOT write this — your job is to **break it**, not defend it.

Target document: `$ARGUMENTS`

## Stance (read before anything)

- Adopt a **skeptical reviewer** persona. Assume the spec is wrong until each part survives scrutiny.
- Your goal is to surface **holes, hidden assumptions, and failure modes** — not to re-design from scratch and not to re-ask questions the spec already answers.
- This is the separation-of-concerns pass: the spec was authored in one context; you verify it in a fresh, adversarial one. Never rubber-stamp.
- Use the `grill-me` skill's core method (relentless, one-question-at-a-time interview down each branch of the decision tree, with your recommended answer attached to every question). This command narrows that method to *attacking an existing artifact* and *persisting the result*.

## Step 1 — Resolve the target

1. If `$ARGUMENTS` names a file, use it.
2. Otherwise, look for the most recently modified design/spec/plan, in this order:
   - `docs/superpowers/specs/*.md`
   - `docs/superpowers/plans/*.md`
   - `docs/plans/*.md` / `docs/specs/*.md`
   - any `*-design.md` / `*-spec.md` / `*-plan.md` in the repo
3. If nothing is found, STOP and ask the user for the path. Do not invent a document.

Read the **entire** target document before asking anything.

## Step 2 — Map the attack surface

Explore the codebase to ground your critique (do NOT ask the user what the code can answer). Then build a private list of weak points to interrogate. For feature/DB/schema work, deliberately probe:

- **Migration safety** — forward/backward migration, ordering, locking, large-table impact, zero-downtime
- **Backward compatibility** — existing readers/writers, API contracts, serialized data, feature flags
- **Data integrity** — constraints, nullability, uniqueness, FK/cascade behavior, partial-failure states
- **Rollback** — can this be reverted after deploy? what becomes irreversible (dropped columns, backfills)?
- **Failure modes & concurrency** — retries, idempotency, race conditions, partial writes
- **Edge cases** — empty/huge inputs, boundary values, timezone/encoding, multi-tenant isolation
- **Hidden assumptions** — anything stated as obvious that isn't verified by code or data
- **Scope & YAGNI** — speculative features, over-abstraction, things that should be split out
- **Testability** — what observable behavior proves it works; is each module testable in isolation?
- **Ambiguity** — any requirement that two engineers could implement differently

## Step 3 — Grill, one question at a time

Walk down each branch of the decision tree, resolving dependencies between decisions first.

- Ask **exactly one question per message**. Prefer multiple-choice when possible.
- For every question, **state your recommended answer and the reasoning** (lead with the recommendation).
- Frame each question as an attack: "The spec assumes X — what happens when ¬X?" rather than open brainstorming.
- If a question is answerable from the codebase, answer it yourself by exploring — don't offload it to the user.
- Keep going until each branch reaches a resolved, defensible decision. Do not stop early because it "looks fine."

## Step 4 — Write resolutions back into the document (critical)

As each point is resolved, **edit the target file in place** so the refinement is not lost:

- Fold confirmed decisions into the relevant section (Implementation Decisions / Testing Decisions / etc.).
- Add an `## Adversarial Review` section near the end capturing: what was challenged, the resolution, and any remaining risks / explicitly-accepted tradeoffs.
- Tighten any requirement you found ambiguous so it can only be read one way.
- Mark anything the user chose to defer as **Out of Scope** with a one-line reason.

Never let a verbal conclusion stay verbal — if it changed the design, it changes the file.

## Step 5 — Consistency sweep

Re-read the edited document with fresh eyes:

1. **Placeholder scan** — no TBD/TODO/vague requirements left.
2. **Internal consistency** — sections don't contradict each other; architecture matches the feature list.
3. **Scope check** — still focused enough for one implementation cycle, or does it need decomposition?

Fix issues inline.

## Step 6 — Commit and report

1. Stage and commit the updated document only (do not bundle unrelated changes). Commit message:
   `docs(spec): adversarial review of <topic>` — English, no Co-Authored-By line.
2. Report a short summary: **what was challenged**, **what changed in the doc**, **remaining accepted risks**, and the **recommended next step** (e.g. `writing-plans` / `/to-prd` / `/refine-plan`).

## Guardrails

- This is a verification pass — do **not** write implementation code, scaffold, or invoke any implementation skill.
- Stay surgical: edit only the target document and only where the review changed a decision.
- If the review reveals the work is genuinely multiple independent subsystems, say so and recommend decomposing into separate specs before proceeding.
