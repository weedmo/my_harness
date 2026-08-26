---
name: resolving-merge-conflicts
description: "Use when you need to resolve an in-progress git merge/rebase conflict. On OpenCode and Claude Code, direct invocation automatically routes semantic conflict resolution to a deep model."
---

## Standalone routing (OpenCode, Claude Code)

When this skill is invoked directly and the `matt-*` subagent types are available (OpenCode, or the `matt-loop:matt-*` agents on Claude Code — each fixes its own model and reasoning effort, so never add a `model` override), delegate the entire workflow before inspecting or editing conflicts:

- Use `matt-deep` by default.
- Use `matt-free` instead when the user explicitly requested free-only models. If that agent is unavailable, stop and report the blocker; never fall back to a potentially paid model.
- Include the user's request, merge/rebase state, repository path, and the exact instruction: `ROUTED_EXECUTION=1; use $resolving-merge-conflicts and complete the conflict resolution.`
- Wait for the routed agent and report its result. Do not duplicate its work in the caller.

If `ROUTED_EXECUTION=1` is already present, or another skill invoked this as one of its internally routed steps, execute locally and do not delegate again. In normal routing, if the named agent is unavailable, continue locally and report that routing was unavailable.

1. **See the current state** of the merge/rebase. Check git history, and the conflicting files.

2. **Find the primary sources** for each conflict. Understand deeply why each change was made, and what the original intent was. Read the commit messages, check the PRs, check original issues/tickets.

3. **Resolve each hunk.** Preserve both intents where possible. Where incompatible, pick the one matching the merge's stated goal and note the trade-off. Do **not** invent new behaviour. Always resolve; never `--abort`.

4. Discover the project's **automated checks** and run them — typically typecheck, then tests, then format. Fix anything the merge broke.

5. **Finish the merge/rebase.** Stage everything and commit. If rebasing, continue the rebase process until all commits are rebased.
