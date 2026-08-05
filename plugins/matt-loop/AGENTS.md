# matt-loop for Codex

This package exposes the matt loop (`matt-auto` plus the vendored Matt Pocock skills) for Codex.

Run `$matt-auto` to take an idea through Matt Pocock's main flow — grilling interview, spec, tracer-bullet tickets, per-ticket implementation — pausing only where a human decision is required. The vendored skills (`$grill-me`, `$implement`, `$code-review`, ...) remain directly invocable for partial work. When a skill mentions Claude-specific hooks, slash commands, or `~/.claude` paths, treat that as Claude-oriented guidance rather than a guaranteed Codex runtime feature.

This Codex package does not ship the repository's Claude hook automation.
