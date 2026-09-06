---
name: resolving-merge-conflicts
description: "Use when you need to resolve an in-progress git merge/rebase conflict. Claude Code edition: direct invocation delegates the resolution to the matt-deep plugin agent."
---

## Routing (Claude Code)

When this skill is invoked directly, delegate the entire resolution to `matt-loop:matt-deep` before inspecting or editing conflicts: spawn it by name with no `model` override, put the merge/rebase state, the repository path, and the user's request in the prompt with the instruction `use $resolving-merge-conflicts and complete the conflict resolution`, wait for it, and report its result without duplicating its work. If the plugin agent is unavailable, use the Agent tool with `model: fable`, `effort: high` and report the fallback.

When already running inside a routed agent (the prompt carries that instruction, or another skill dispatched this as one of its steps), execute the steps below locally and do not delegate again.

1. **See the current state** of the merge/rebase. Check git history, and the conflicting files.

2. **Find the primary sources** for each conflict. Understand deeply why each change was made, and what the original intent was. Read the commit messages, check the PRs, check original issues/tickets.

3. **Resolve each hunk.** Preserve both intents where possible. Where incompatible, pick the one matching the merge's stated goal and note the trade-off. Do **not** invent new behaviour. Always resolve; never `--abort`.

4. Discover the project's **automated checks** and run them — typically typecheck, then tests, then format. Fix anything the merge broke.

5. **Finish the merge/rebase.** Stage everything and commit. If rebasing, continue the rebase process until all commits are rebased.
