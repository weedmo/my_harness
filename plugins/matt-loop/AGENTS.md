# matt-loop for Codex

This package exposes the matt loop (`matt-auto` plus the vendored Matt Pocock skills) for Codex.

Run `$matt-auto` to take an idea through Matt Pocock's main flow — grilling interview, spec, tracer-bullet tickets, per-ticket implementation. A decision delegate answers implementation-level questions on your behalf; material decisions escalate immediately, and you confirm once before tickets publish. OpenCode installations route subagent work by task tier automatically; other platforms retain their normal effort selection. On platforms without subagents the flow falls back to fully human-in-the-loop. The vendored skills (`$grill-me`, `$implement`, `$code-review`, ...) remain directly invocable for partial work. When a skill mentions Claude-specific hooks, slash commands, or `~/.claude` paths, treat that as Claude-oriented guidance rather than a guaranteed Codex runtime feature.

This Codex package does not ship the repository's Claude hook automation.
