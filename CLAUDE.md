# Behavioral Guidelines

Reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

# weed-harness - Global Rules

## Parallel Execution

Always run **independent tasks in parallel**. Never serialize work that has no dependencies.

| Parallel OK | Must be Sequential |
|-------------|-------------------|
| Editing different files/modules | Edit A → test A |
| Code analysis + doc analysis | Analysis → implementation plan |
| Independent module refactors | DB schema change → ORM update |

## Branch Workflow (Mandatory)

When starting development work in a git repo connected to GitHub:
1. **MUST** check the current branch with `git branch` and `git remote -v`
2. **MUST** ask the user before writing any code:
   - Which branch to base the work on (e.g., `main`, `develop`, existing feature branch)
   - What to name the new branch (or whether to work on the current branch)
3. **Do NOT** proceed with any code changes until the user confirms the branch setup
4. Create and checkout the branch only after user confirmation

## Git Commits

Do NOT include `Co-Authored-By` lines in commit messages.

## Auto-Fix After Review (Mandatory)

When reviewing code and finding issues:
1. **Fix all issues immediately** without asking the user for permission.
2. After fixing, **run relevant tests**. If tests fail, fix them too.
3. Never say "수정할까요?" or "진행할까요?" — just fix it.
4. The Edit/Write PostToolUse hook will trigger auto-review on your fixes.

# graphify
- **graphify** (`~/.claude/skills/graphify/SKILL.md`) - any input to knowledge graph. Trigger: `/graphify`
When the user types `/graphify`, invoke the Skill tool with `skill: "graphify"` before doing anything else.

## graphify operating policy (codebase knowledge graph)

graphify is the standard knowledge-graph backbone for codebases here. The goal is
two-fold and matters more as a project grows: **token savings** for agent retrieval
and **fast human comprehension**. Apply this policy.

- **Distribution**: graphify is the pip package `graphifyy`, and
  `graphify install --platform claude` / `--platform codex` generates the local
  skill for each platform. The package version IS the skill version. A
  SessionStart hook (`~/.claude/hooks/auto-update.sh`) AUTO-applies newer PyPI
  versions and re-installs the skill for both claude and codex; it also updates
  the superpowers plugin and re-syncs the matt-* codex skills.
- **Build for both audiences**: `graphify <repo> --directed --wiki`. `--directed`
  preserves call direction (matters for code); `--wiki` emits an agent-crawlable
  wiki that humans also read. Outputs land in `graphify-out/` (+ HTML / Obsidian
  vault for human browsing).
- **Keep it fresh (critical long-term)**: a stale graph lies. Run `--update`
  (incremental, changed files only) in CI / on commit, and `--watch` locally.
  Never rely on a one-time build for an evolving codebase.
- **Agent retrieval = token savings**: when `graphify-out/graph.json` exists, treat
  natural-language questions about the codebase as graphify queries
  (`graphify query "..." --budget N`, `--dfs` to trace a path) instead of reading
  whole files. Optionally expose query/path/explain to agents via `graphify --mcp`.
- **Honest limits**: the graph is for orientation (where is X, how is it connected).
  Precise references ("all callers of f") are better from LSP/Sourcegraph, and
  actual edits / deep logic verification still require Claude Code reading the real
  source — the graph narrows that reading to save tokens, it does not replace it.
