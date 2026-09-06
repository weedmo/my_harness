---
name: model-routing
description: "Codex · OpenCode · Orca only; the Claude Code editions route by their agent files and never read this. Two tiers, Default and Deep, their pair per platform and as Orca worker flags, dispatch rules, the one-step ladder. Reference skill, never invoked standalone."
---

# Model routing (shared)

Classify from the actual task, not keywords; take the lowest tier that is clearly sufficient. A loop's SKILL.md maps its *roles* to a tier here, plus any cap or reservation; pairs, dispatch, and the ladder live only here, so a rename is one edit.

## Tiers

| Tier | Codex `spawn_agent` | Claude Code agent | OpenCode | Use when |
|---|---|---|---|---|
| Default | gpt-6-astra / medium | opus / medium | gpt-5.6-terra / medium | Feature work, tests, moderate refactors, small fixes, mechanical edits |
| Deep | gpt-6-astra / high | fable / high | gpt-5.6-sol / high | Hard debugging, architecture, migrations, algorithms, concurrency, invariants, demanding review, whole-run decisions |
| Large context | chunk via Deep | chunk via Deep | Gemini | Repository-scale discovery; large documents, logs, media |

- Codex: one model, the tier *is* the effort. Design decisions never go below Deep.
- OpenCode's `openai` provider lacks gpt-6-astra (2026-09-06); it keeps the 5.6 pairs.
- Both plausible → Default; a persistent whole-run role → Deep.
- **Ladder, one step.** Default reports genuinely difficult reasoning → retry once on Deep. Deep reports the problem beyond it → Codex calls the *same* agent once more with `reasoning_effort: "max"`; Claude Code and OpenCode stop there as a handoff. A loop may reserve the Codex `max` retry for one role (autocode's strategist).
- **No `ultra` in a loop.** Astra's `ultra` delegates inside the worker, outside the loop's worktrees, measurement, and re-verification. `max` is the Codex ceiling; `ultra` is for the user's own session.
- **Large context.** Chunk the material, summarize each chunk with source references on the routed agent, synthesize on Deep. OpenCode does the same when its Gemini agent cannot start; Gemini CLI is never needed.

## Dispatch per platform

- **Codex** — `spawn_agent` with `model: "gpt-6-astra"`, the tier's `reasoning_effort`, `fork_turns: "none"` (an override cannot ride a full-history fork), and a prompt carrying every path, ticket/spec reference, user constraint, and `ROUTED_EXECUTION=1`. A persistent role gets a brief; keep its agent id and continue it with `send_message`, never respawn per question.
- **Claude Code** — the loop's agents fix model and effort (`matt-loop:matt-default` / `matt-deep`, `auto-loop:experimenter-default` / `experimenter-deep` / `strategist`). Spawn by name, no `model` override.
- **OpenCode** — the packaged subagents (`matt-default` / `matt-deep` under `~/.config/opencode/agents/`); without them, the normal subagent, tier named in the prompt.
- **Orca workers** (`orca orchestration worker-start`) — Codex `--agent codex --model gpt-6-astra --effort medium|high`; `--effort max` only with `--retry-of <dispatch>` after Deep reported the problem beyond it. Claude Code `--agent claude --model opus --effort medium` (Default), `--agent claude --model claude-fable-5-1 --effort high` (Deep). OpenCode `--agent opencode` with `ROUTED_EXECUTION=1; use <tier agent>` in the prompt (no model flags reach opencode). Rejected pair → retry without `--effort`; rejected flags → start without them, tier in the prompt; note it on the board.
- **Other platforms, or an unavailable route** — the normal subagent, tier in the prompt, fallback reported once; never a silent swap.
- **Free-only mode** — only the loop's free set (matt-loop's `matt-free` / `matt-free-fast` on OpenCode); a missing free agent stops the run rather than paying. Elsewhere, say it has no route and route normally.

## Red flags

- Asking the user for an effort on Codex, OpenCode, or Claude Code → routing is automatic there.
- A `model` override on a Claude Code routing agent → the agent already fixes both.
- Two retries on a rung, or Codex `max` after a Default failure → one step at a time.
- A routed role on `ultra`, Deep because the task sounds important, a loop with its own pairs → the loop owns orchestration; classify from need; map roles to tiers.
- Guessing pairs when this skill is missing → say `model-routing unavailable — using the platform's normal subagent for every role` once and continue.
