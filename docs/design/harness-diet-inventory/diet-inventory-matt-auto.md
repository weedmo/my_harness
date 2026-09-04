# matt-auto rule inventory (before diet)


## Rules
1. [Rules] Invoke each stage's skill and follow it exactly. Do not reimplement, merge, or "improve" a
2. [Rules] Wherever a sub-skill puts a question to "the user" — interview questions, seam check, tick
3. [Rules] Discoverable facts are still looked up in the environment, never asked. This is grilling's
4. [Rules] Do not add gates or scores the vendored skills don't define. Artifacts are theirs — `CONTE

## Pipeline
5. [Pipeline] step 1 Precondition
6. [Pipeline] step 2 Select routing
7. [Pipeline] step 3 Spawn the decision delegate
8. [Pipeline] step 4 Interview
9. [Pipeline] step 5 Size branch
10. [Pipeline] step 6 Spec
11. [Pipeline] step 7 Tickets
12. [Pipeline] step 8 Confirm (`--confirm` only; human, once)
13. [Pipeline] step 9 Implement loop
14. [Pipeline] step 10 Ship (only with `--dev` / `--main` / `--pr <base>`)

## Progress board
15. [Progress board] Statuses: `✅` done · `🔄` in progress (append a short note of what exactly, e.g. the curren
16. [Progress board] Skill / route names the vendored skill driving the stage and, once known, the routed agent
17. [Progress board] Small path (step 5 fits one session): mark 6–9 `⏭️ small path`; the board ends at step 5, 
18. [Progress board] Step 10's note tracks the babysit cycle (e.g. `🔄 cycle 2/5: CI red`, `🔄 resolving conflict
19. [Progress board] Worker is the Orca dispatch id, worktree, and (when remote) the environment; `—` for a tic
20. [Progress board] Gates is the unlazy ledger tally from the latest `--reverify` (`met/total`); `—` when unla
21. [Progress board] In ship mode, step 10's note also carries the ship ledger tally from the latest `--reverif
22. [Progress board] In autonomous mode (the default), also append one stage-transition line per board update t
23. [Progress board] Every board update also republishes the artifact once tickets exist — see Live board in th

## Model routing (Codex, OpenCode, Claude Code)
24. [Model routing (Codex, OpenCode, Claude Code)] Classify each ticket and each standalone task from what it actually needs, lowest clearly 
25. [Model routing (Codex, OpenCode, Claude Code)] If a named routing agent or Codex model override is unavailable, fall back to the platform

## Delegate brief
26. [Delegate brief] You answer implementation-level questions on the user's behalf with senior-engineer judgme
27. [Delegate brief] Reply with the decision plus a one-line rationale. Your log is shown to the user verbatim,
28. [Delegate brief] Never decide these yourself; reply `ESCALATE: <why>` instead — security, data meaning or m

## Escalation

## Autonomous by default (`--confirm` to opt out)
29. [Autonomous by default (`--confirm` to opt out)] Step 2 (routing)
30. [Autonomous by default (`--confirm` to opt out)] Steps 5 and 8 (confirms)
31. [Autonomous by default (`--confirm` to opt out)] Step 4's interview gate is never skipped
32. [Autonomous by default (`--confirm` to opt out)] Escalation is untouched.
33. [Autonomous by default (`--confirm` to opt out)] Decision log

## Live board in the artifact
34. [Live board in the artifact] When to republish:
35. [Live board in the artifact] What "blocked" means here:
36. [Live board in the artifact] `progress.current`
37. [Live board in the artifact] Every ticket node carries who is running it
38. [Live board in the artifact] Percentages and ETA come from the data, not from you.
39. [Live board in the artifact] The plan is published before implementation starts
40. [Live board in the artifact] The flow does not end at the last ticket.
41. [Live board in the artifact] Each ticket node opens a detail modal
42. [Live board in the artifact] The terminal board stays exactly as it is; this mirrors it, never replaces it. When `$inte

## Final report (before → after)
43. [Final report (before → after)] Measure, never estimate.
44. [Final report (before → after)] Classify each file
45. [Final report (before → after)] Then report in the terminal

## Interview gate (never skipped)
46. [Interview gate (never skipped)] Deliver where the user reads, not a file path.
47. [Interview gate (never skipped)] Wait.
48. [Interview gate (never skipped)] Say how to answer.
49. [Interview gate (never skipped)] Clearing it.
50. [Interview gate (never skipped)] This is the only gate autonomous mode keeps. Steps 5 and 8 stay skipped, and escalation st

## Decision-graph report
51. [Decision-graph report] Generate
52. [Decision-graph report] Round-trip.
53. [Decision-graph report] The final regeneration carries the `outcome` block
54. [Decision-graph report] The final report still summarizes outcomes in the terminal, but points at the graph for th

## Ship mode (`--dev` / `--main` / `--pr <base>`)
55. [Ship mode (`--dev` / `--main` / `--pr <base>`)] PR branch.
56. [Ship mode (`--dev` / `--main` / `--pr <base>`)] PR condition.
57. [Ship mode (`--dev` / `--main` / `--pr <base>`)] Ship ledger (when the unlazy skill is installed).
58. [Ship mode (`--dev` / `--main` / `--pr <base>`)] Open the PR.
59. [Ship mode (`--dev` / `--main` / `--pr <base>`)] Babysit.
60. [Ship mode (`--dev` / `--main` / `--pr <base>`)] Conflicts.
61. [Ship mode (`--dev` / `--main` / `--pr <base>`)] Merge-ready, not merged.
62. [Ship mode (`--dev` / `--main` / `--pr <base>`)] Routing.
63. [Ship mode (`--dev` / `--main` / `--pr <base>`)] Report.

## Parallel execution (automatic)
64. [Parallel execution (automatic)] Start from `$to-tickets`' blocking edges: tickets whose blockers are all satisfied form a 
65. [Parallel execution (automatic)] Keep a candidate **sequential** when the tickets touch the same files or the same section 
66. [Parallel execution (automatic)] Cap a parallel wave at the plan's concurrency (default 2, max 4), and prefer fewer, wider 
67. [Parallel execution (automatic)] Give every ticket an `estimateMin` — your own honest guess at its size, which the page ren
68. [Parallel execution (automatic)] With Orca unreachable, every wave is `sequential` and the plan says why in `note`. The pla
69. [Parallel execution (automatic)] What it is.
70. [Parallel execution (automatic)] Preconditions
71. [Parallel execution (automatic)] Routing → worker flags.
72. [Parallel execution (automatic)] The loop (step 9).
73. [Parallel execution (automatic)] Ship (step 10).
74. [Parallel execution (automatic)] unlazy boundaries.
75. [Parallel execution (automatic)] Report and log.

## Fallback
76. [Fallback] Platform without subagents: run the flow human-in-the-loop instead — every sub-skill quest
77. [Fallback] Delegate lost mid-pipeline: respawn it with the Q&A log so far as context.
78. [Fallback] weed-harness shared skills missing (`$loop-report`, `$model-routing`, `$loop-gates`): say 

## Red flags — you are drifting off the flow
79. [Red flags — you are drifting off the flow] Answering a sub-skill's question yourself instead of routing it to the delegate → the dele
80. [Red flags — you are drifting off the flow] Publishing tickets before step 8's confirm in `--confirm` mode → that confirm is the gate 
81. [Red flags — you are drifting off the flow] Letting the artifact go stale while the terminal board moves on, or marking a ticket `bloc
82. [Red flags — you are drifting off the flow] Dropping the live board or the final before → after report because the artifact link was r
83. [Red flags — you are drifting off the flow] Running `orca artifacts`, `tab create`, or `reload --page` from here → delivery has one ow
84. [Red flags — you are drifting off the flow] Reporting file or line counts that were not measured from `git diff --numstat` against ste
85. [Red flags — you are drifting off the flow] Starting the spec, tickets, or `$implement` while the interview gate is unanswered → that 
86. [Red flags — you are drifting off the flow] Treating autonomous mode as license to skip escalation too → it removes the effort questio
87. [Red flags — you are drifting off the flow] Running autonomously without a decision log file, or letting it fall behind → it's the onl
88. [Red flags — you are drifting off the flow] Reporting decisions as prose instead of the decision-graph HTML, or finishing a run while 
89. [Red flags — you are drifting off the flow] Asking the user mid-pipeline about non-material decisions → that is the delegate's job now
90. [Red flags — you are drifting off the flow] Scoring ambiguity percentages or inventing readiness gates → no Matt skill does this. Drop
91. [Red flags — you are drifting off the flow] Marking a ticket complete while its unlazy ledger has unmet gates, or trusting the subagen
92. [Red flags — you are drifting off the flow] Writing specs or notes outside the tracker, `CONTEXT.md`/ADRs, the decision log, or `$inte
93. [Red flags — you are drifting off the flow] Running several implementation workers in parallel outside a wave the plan declared parall
94. [Red flags — you are drifting off the flow] Creating a parallel wave's workers with a non-Orca subagent tool and calling it orchestrat
95. [Red flags — you are drifting off the flow] Stopping or abandoning an Orca worker because of a timeout, idle TUI, or heartbeat → those
96. [Red flags — you are drifting off the flow] Starting an Orca worker for work that runs alone — the small path, a sequential wave's tic
97. [Red flags — you are drifting off the flow] Merging a worker's branch on its `worker_done` alone, or marking a ticket done before the 
98. [Red flags — you are drifting off the flow] Letting the progress board go stale, inventing a per-platform format for it, or writing it
99. [Red flags — you are drifting off the flow] Opening a PR without `--dev` / `--main` / `--pr <base>`, or opening it before the PR condi
100. [Red flags — you are drifting off the flow] Merging the PR, force-pushing the PR branch, or rebasing it to clear a conflict → merge-re
101. [Red flags — you are drifting off the flow] Calling the PR merge-ready from local checks, your own reading of the checks page, or pr-b
102. [Red flags — you are drifting off the flow] Opening the PR while a PR-condition gate is unmet or was "met" by the delegate's say-so → 
