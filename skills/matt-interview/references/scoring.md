# Implementation ambiguity scoring

Score each dimension from `0.0` to `1.0` using evidence from the user, repository, tests, and primary documentation.

| Score | Meaning |
| --- | --- |
| `0.00` | Unknown or contradictory |
| `0.25` | Vague direction without an actionable example |
| `0.50` | Partially specified; multiple material implementations remain |
| `0.75` | Mostly specified; one material decision or scenario remains |
| `0.90` | Implementation-ready; only local, reversible choices remain |
| `1.00` | Explicit, testable, and evidence-backed |

Use these fixed weights:

| Dimension | Weight | Critical |
| --- | ---: | :---: |
| Intent | 0.10 | No |
| Outcome | 0.10 | No |
| Scope | 0.15 | Yes |
| Behavior | 0.15 | Yes |
| Domain and data | 0.10 | No |
| Interfaces and integrations | 0.15 | Yes |
| Constraints and operations | 0.10 | No |
| Verification | 0.15 | Yes |

Calculate:

`ambiguity = 1 - sum(score × weight)`

Do not let the weighted average hide one dangerous gap. Scope, Behavior, Interfaces and integrations, and Verification must each score at least `0.80`.

Required Boolean gates:

- `non_goals`
- `decision_boundaries`
- `acceptance_criteria`
- `fact_grounding`
- `pressure_pass`

Keep `blocking_unknowns` at zero. A blocking unknown is an unanswered question whose alternatives would change externally visible behavior, scope, a public interface, data meaning or migration, security/privacy, irreversible operations, or acceptance criteria.

Discoverable repository facts are not blocking unknowns; investigate them. Ordinary implementation choices are not blocking when the Decision Boundaries explicitly delegate them.

Interpret `fact_grounding` as follows:

- **Brownfield:** inspect the relevant code, tests, repository rules, and nearby contracts; mark conflicting claims as unresolved.
- **Greenfield:** verify external capabilities, standards, limits, and version-sensitive feasibility with primary sources when they constrain the design.
- **Both:** treat user-owned goals, preferences, policy, and business rules as decisions rather than facts needing external proof.

Set `fact_grounding: false` while any material feasibility claim is merely assumed. Do not require research for local, reversible implementation choices already delegated by Decision Boundaries.

The `pressure_pass` gate means at least one earlier user answer was revisited by one later user-facing question and materially clarified. It does not require a second question inside every round.

## Script input

Pass a JSON object with exact dimension and gate keys:

```json
{
  "scores": {
    "intent": 0.9,
    "outcome": 0.9,
    "scope": 0.9,
    "behavior": 0.9,
    "domain_data": 0.9,
    "interfaces": 0.9,
    "constraints_operations": 0.9,
    "verification": 0.9
  },
  "gates": {
    "non_goals": true,
    "decision_boundaries": true,
    "acceptance_criteria": true,
    "fact_grounding": true,
    "pressure_pass": true
  },
  "blocking_unknowns": []
}
```

Run:

```text
python <skill-dir>/scripts/score_ambiguity.py --input-json <json>
```

Use the returned `eligible_for_implementation` value as the quantitative gate. Explain each score in the transcript; the script verifies arithmetic, not judgment.

If only a previous aggregate ambiguity is available and dimension scores are missing, do not derive a new percentage. Restore the dimension breakdown or set readiness false until it can be rescored.
