# matt-loop for Codex

This package exposes the matt loop (`matt-auto`, PR babysitting, routed conflict resolution, and the vendored Matt Pocock skills) for Codex and other supported agents.

Run `$matt-auto` to take an idea through Matt Pocock's main flow — grilling interview, spec, tracer-bullet tickets, per-ticket implementation. Use `$pr-babysit` for one open PR and `$resolving-merge-conflicts` for an active merge/rebase conflict. OpenCode installations route these standalone workflows and matt-auto subagent work by task tier automatically; other platforms use their normal agents. Material decisions still escalate to the user. The vendored skills (`$grill-me`, `$implement`, `$code-review`, ...) remain directly invocable for partial work. When a skill mentions Claude-specific hooks, slash commands, or `~/.claude` paths, treat that as Claude-oriented guidance rather than a guaranteed Codex runtime feature.

This Codex package does not ship the repository's Claude hook automation.
