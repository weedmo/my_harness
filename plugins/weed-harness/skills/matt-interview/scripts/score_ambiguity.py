#!/usr/bin/env python3
"""Calculate the matt-interview implementation-readiness gate."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


WEIGHTS = {
    "intent": 0.10,
    "outcome": 0.10,
    "scope": 0.15,
    "behavior": 0.15,
    "domain_data": 0.10,
    "interfaces": 0.15,
    "constraints_operations": 0.10,
    "verification": 0.15,
}

CRITICAL_DIMENSIONS = ("scope", "behavior", "interfaces", "verification")
REQUIRED_GATES = (
    "non_goals",
    "decision_boundaries",
    "acceptance_criteria",
    "fact_grounding",
    "pressure_pass",
)
THRESHOLD = 0.10
CRITICAL_MINIMUM = 0.80


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Score implementation ambiguity from matt-interview JSON."
    )
    parser.add_argument("--input-json", required=True, help="JSON scoring payload")
    return parser.parse_args()


def require_mapping(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be an object")
    return value


def main() -> int:
    args = parse_args()
    try:
        payload = json.loads(args.input_json)
        if not isinstance(payload, dict):
            raise ValueError("input must be a JSON object")

        scores = require_mapping(payload, "scores")
        gates = require_mapping(payload, "gates")
        unknowns = payload.get("blocking_unknowns", [])
        if not isinstance(unknowns, list):
            raise ValueError("blocking_unknowns must be an array")

        if set(scores) != set(WEIGHTS):
            missing = sorted(set(WEIGHTS) - set(scores))
            extra = sorted(set(scores) - set(WEIGHTS))
            raise ValueError(f"score keys mismatch; missing={missing}, extra={extra}")
        if set(gates) != set(REQUIRED_GATES):
            missing = sorted(set(REQUIRED_GATES) - set(gates))
            extra = sorted(set(gates) - set(REQUIRED_GATES))
            raise ValueError(f"gate keys mismatch; missing={missing}, extra={extra}")

        normalized_scores: dict[str, float] = {}
        for name, raw_value in scores.items():
            if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float)):
                raise ValueError(f"score {name} must be numeric")
            value = float(raw_value)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"score {name} must be between 0 and 1")
            normalized_scores[name] = value

        for name, value in gates.items():
            if not isinstance(value, bool):
                raise ValueError(f"gate {name} must be Boolean")

        weighted_clarity = sum(
            normalized_scores[name] * weight for name, weight in WEIGHTS.items()
        )
        ambiguity = max(0.0, min(1.0, 1.0 - weighted_clarity))
        failed_critical = [
            name
            for name in CRITICAL_DIMENSIONS
            if normalized_scores[name] < CRITICAL_MINIMUM
        ]
        failed_gates = [name for name in REQUIRED_GATES if not gates[name]]
        eligible = (
            ambiguity <= THRESHOLD + 1e-12
            and not failed_critical
            and not failed_gates
            and not unknowns
        )

        result = {
            "weighted_clarity": round(weighted_clarity, 4),
            "ambiguity": round(ambiguity, 4),
            "ambiguity_percent": round(ambiguity * 100, 2),
            "threshold": THRESHOLD,
            "critical_minimum": CRITICAL_MINIMUM,
            "failed_critical_dimensions": failed_critical,
            "failed_gates": failed_gates,
            "blocking_unknowns": unknowns,
            "eligible_for_implementation": eligible,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (json.JSONDecodeError, ValueError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
