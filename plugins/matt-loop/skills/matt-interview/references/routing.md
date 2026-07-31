# Matt skill routing

Use the smallest set that resolves real ambiguity.

| Signal | Skill | Interview use |
| --- | --- | --- |
| Interview pressure and branching decisions | `$grilling` | Ask one question at a time, include a recommendation, and walk dependencies in order. |
| Brownfield interview with deliberate glossary/ADR updates | `$grill-with-docs` | Use only when the user opts into those durable documentation updates. |
| No codebase | `$grill-me` | Use the stateless grilling flow. |
| Correct Matt flow is unclear | `$ask-matt` | Run explicitly as a router; it cannot trigger implicitly. |
| Terms, invariants, relationships, or lifecycle are fuzzy | `$domain-modeling` | Challenge language and stress scenarios. Update `CONTEXT.md` or ADRs only when the user opted into durable docs. |
| Module shape, interface, seam, or testability is unclear | `$codebase-design` | Clarify the smallest useful interface and where behavior should be observed. |
| A hard existing bug motivates the change | `$diagnosing-bugs` | Establish the exact symptom and feedback loop before interviewing about the fix. |
| Test strategy or acceptance evidence is unclear | `$tdd` | Agree public test seams and behavioral examples; do not implement during the interview. |
| A runnable answer is required | `$prototype` | Hand off one bounded design question to throwaway code, then resume with the finding. |
| External technical facts are uncertain | `$research` | Gather primary-source evidence before asking the user to decide. |
| Ready implementation is multi-track | `$matt-orchestrator` | Execute only after ambiguity and readiness gates pass. |

Do not run skills ceremonially. The interview owns user decisions; supporting skills provide evidence, vocabulary, or a bounded experiment.
