---
name: model-routing
description: "The shared model/effort routing table for every delegated loop in this harness (matt-auto, pr-babysit, resolving-merge-conflicts, autocode) — four tiers (Fast / Default / Deep / Max) with the exact model and reasoning-effort pair each resolves to on Codex, Claude Code, OpenCode, and as Orca worker-start flags, plus the dispatch rules and the escalation ladder. A loop maps its own roles onto these tiers and dispatches through this table; it never invents its own pairs. Reference skill: read it when routing, do not invoke it standalone."
---

# Model routing (shared)

Classify from the actual task, not keyword matching, and use the lowest tier that is clearly sufficient. Tier names and thresholds are the same on every platform; only the dispatch mechanism differs. A loop defines *roles* (matt-auto's delegate and implementers, autocode's strategist and experimenters) and maps each role to a tier here — the pairs below are the only ones any loop uses.

## Tiers

| Tier | Codex `spawn_agent` | Claude Code agent | OpenCode | Use when |
|---|---|---|---|---|
| Fast | gpt-6-astra / low | haiku / low | gpt-5.6-luna / low | Small bug fixes, type errors, focused tests, boilerplate, one-site mechanical edits |
| Default | gpt-6-astra / medium | opus / medium | gpt-5.6-terra / medium | Ordinary feature work, tests, moderate refactors, multi-site changes inside a module, code-plus-doc tasks |
| Deep | gpt-6-astra / high | fable / high | gpt-5.6-sol / high | Difficult debugging, architecture, broad refactors, migrations, algorithm replacement, concurrency, invariants, demanding review, any role that makes design decisions for a whole run |
| Max | gpt-6-astra / max | fable / xhigh | — (retry Deep) | Only as the retry tier when Deep reports the problem is beyond it, or for a role a loop explicitly reserves for it (autocode's escalated strategist) |
| Large context | chunk via Max | chunk via Max | Gemini | Repository-scale discovery or large PDF, image, video, log, or document analysis |

- On Codex every tier is the same model; the tier *is* the reasoning effort. `xhigh` is not a tier, and `ultra` is never used for a routed role (see the ladder). On Claude Code the coordinator normally runs on Fable, so a tier below Deep is a deliberate step down for a task that clearly does not need the coordinator's model — never route a design decision below Deep.
- OpenCode's `openai` provider does not expose gpt-6-astra (checked 2026-09-06: `opencode models` lists only the 5.6 family), so OpenCode stays on the 5.6 pairs until it appears; then it takes the Codex column.
- Default to **Default** when two tiers are plausible. Use **Deep** for any persistent role that makes decisions across a whole run (a decision delegate, a strategist) — it is cheap relative to a wrong plan.
- **Escalation ladder.** If a Fast agent reports the task exceeds its scope, retry once on Default. If Default identifies a genuinely difficult reasoning problem, retry once on Deep. On Codex or Claude Code, if Deep in turn reports the problem is beyond it, retry once on Max; that is the only automatic path to Codex `max` or Claude `xhigh`. On OpenCode, Deep is the ceiling. A loop may cap a role lower (autocode caps experimenters at Deep) — say so in the loop.
- **No `ultra` inside a loop.** Astra's `ultra` effort switches on automatic task delegation inside the worker. The loop owns orchestration — worktrees, serial measurement, gate re-verification, the board — and a worker that spawns its own delegates breaks that contract and hides work from the loop. `max` is the Codex ceiling for every routed role; `ultra` is for a user's own interactive session, never for a dispatched worker.
- **Large context.** On Codex and Claude Code there is no separate large-context route: split oversized repositories, documents, or logs into coherent chunks, ask the routed agent to summarize each chunk with source references, then synthesize those summaries in a final routed call on Max. On OpenCode, if the Gemini-backed agent cannot start (provider, credentials, model, or quota), retry the analysis on Deep with the same chunking. This fallback never requires Gemini CLI.

## Dispatch per platform

- **Codex** — `spawn_agent` with `model: "gpt-6-astra"` and `reasoning_effort` set to the tier's effort, and `fork_turns: "none"` for fresh-context workers. A model override cannot be combined with a full-history fork, so put every required path, ticket/spec reference, user constraint, and a `ROUTED_EXECUTION=1` marker in the prompt. A persistent role also uses `fork_turns: "none"` with an explicit brief in its prompt; keep its returned agent id and continue it with `send_message`/`followup_task` — do not respawn it per question.
- **Claude Code** — each loop ships agent definitions that fix both the model and the reasoning effort (`matt-loop:matt-fast` … `matt-loop:matt-max`, `auto-loop:experimenter-fast` … `auto-loop:strategist-max`). Routing a task to an agent *is* choosing its effort: spawn it by name, never pass a `model` override on top, and never ask the user for effort when these agents are present.
- **OpenCode** — use the loop's packaged subagent types (`matt-fast` / `matt-default` / `matt-deep`; the installer places them under `~/.config/opencode/agents/`). A loop without packaged OpenCode agents uses the platform's normal subagent and names the intended tier in the prompt.
- **Orca workers** (`orca orchestration worker-start`) — translate the tier into flags instead of an in-session agent. Under Codex: `--agent codex --model gpt-6-astra --effort <low|medium|high|max>` by tier, `max` only as a `--retry-of` after Deep reports the problem is beyond it. Under Claude Code: Fast → `--agent claude --model haiku` (Orca rejects `--effort` for haiku); Default → `--agent claude --model opus --effort medium`; Deep → `--agent claude --model claude-fable-5-1 --effort high`; Max → `--agent claude --model claude-fable-5-1 --effort xhigh`, same retry rule. Under OpenCode use `--agent opencode` and put `ROUTED_EXECUTION=1; use <the loop's agent for the tier>` in the worker prompt, since Orca does not forward model flags to opencode workers. If Orca rejects a model/effort pair, retry without `--effort` and note it on the board; if the runtime rejects `--model`/`--effort` (older runtime), start the worker without them, name the tier in the prompt, and note the fallback.
- **Any other platform** (no named agents, no model overrides) — use the platform's normal subagent for every role, name the intended tier in the prompt, and say so once at start. Do not silently pick another provider or model.
- **Unavailable route** — if a named agent or a Codex model override is unavailable, fall back to the platform's normal subagent and report the fallback. Never silently substitute a different provider.
- **Free-only mode** — a loop that defines a free route set (matt-loop's `matt-free` / `matt-free-fast` on OpenCode) uses only those routes in that mode and never crosses into a paid tier; if a free agent is unavailable, stop and report rather than fall back to a paid one. Other platforms report that free-only has no route there and continue with normal routing.

## How a loop uses this

Each loop's SKILL.md carries one short table: its role names → the tier here, plus any cap or reservation (retry ceilings, which role gets Max). Everything else — the pairs, the dispatch mechanics, the ladder — is this file, so a model rename is one edit. If this skill is not installed (weed-harness 3.x missing), the loop says `model-routing unavailable — using the platform's normal subagent for every role` once and continues; it does not guess pairs.

## Red flags

- Asking the user which effort to use on Codex, OpenCode, or Claude Code → routing is automatic there; only a platform with neither named agents nor overrides asks, and only when the loop says so.
- Passing a `model` override on top of a Claude Code routing agent → the agent definition already fixes model and effort; the override fights it.
- Retrying on Max after a Fast or Default failure, or more than once per rung → the ladder is one step at a time and Max is reserved for "Deep says it's beyond me".
- Dispatching any routed role on `ultra` → the worker would delegate on its own, outside the loop's worktrees and measurement; `max` is the ceiling.
- Choosing Deep or Max for a task because it sounds important → classify from what the task actually needs; the lowest clearly sufficient tier is the rule.
- A loop carrying its own model/effort pairs → they drift from this table on the next model rename; map roles to tiers instead.
