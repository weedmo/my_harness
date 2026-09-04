"""Experiment-board data checks, run by loop-report's render.py before it writes.

validate(data) -> list of error strings (empty when the data renders right).
The common keys (title, progress, outcome files) are checked by render.py;
this covers what only the experiment board knows about.
"""
import json

DIRECTIONS = {"lower", "higher"}
TIERS = {"deep", "max"}
STATUSES = {"pending", "running", "measured", "keep", "discard", "crash",
            "conflict", "interaction", "cancelled"}
DIFFICULTIES = {"fast", "default", "deep"}
TERMINATED = {"budget_exhausted", "target_reached", "exhausted", "plateau", "paused"}
# These statuses come out of the coordinator's own measurement, so the number
# and the order it was measured in must both be there.
MEASURED = {"keep", "discard", "conflict", "interaction"}


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def validate(d):
    errors = []
    run = d.get("run")
    if not isinstance(run, dict):
        return ["missing top-level key: run (an object)"]
    metric = run.get("metric") or {}
    if not metric.get("name"):
        errors.append("run.metric.name is required")
    if metric.get("direction") not in DIRECTIONS:
        errors.append("run.metric.direction must be one of " + ", ".join(sorted(DIRECTIONS)))
    if not _num(metric.get("baseline")):
        errors.append("run.metric.baseline must be a number (median of three baseline runs)")
    budget = run.get("budget") or {}
    if not isinstance(budget.get("done"), int) or isinstance(budget.get("done"), bool):
        errors.append("run.budget.done must be an integer")
    strategist = run.get("strategist") or {}
    if strategist.get("tier") not in TIERS:
        errors.append("run.strategist.tier must be one of " + ", ".join(sorted(TIERS)))
    reason = run.get("terminatedReason")
    if reason is not None and reason not in TERMINATED:
        errors.append("run.terminatedReason %r is not one of %s" % (reason, sorted(TERMINATED)))
    if d.get("outcome") is not None and reason is None:
        errors.append("outcome present but run.terminatedReason is null — the final regeneration names why the loop stopped")

    seen = set()
    for h in d.get("hypotheses", []) or []:
        if not isinstance(h, dict):
            errors.append("hypothesis is not an object: " + json.dumps(h, ensure_ascii=False)[:80])
            continue
        hid = h.get("id")
        for key in ("id", "claim", "status"):
            if not h.get(key):
                errors.append("hypothesis without " + key + ": " + json.dumps(h, ensure_ascii=False)[:80])
        if hid in seen:
            errors.append("duplicate hypothesis id: " + str(hid))
        seen.add(hid)
        st = h.get("status")
        if st not in STATUSES:
            errors.append("hypothesis %s has unknown status %r" % (hid, st))
        if h.get("difficulty") not in DIFFICULTIES:
            errors.append("hypothesis %s needs difficulty in %s" % (hid, sorted(DIFFICULTIES)))
        if st in MEASURED:
            if not _num(h.get("metric")):
                errors.append("%s hypothesis %s needs a numeric metric (the coordinator's own measurement)" % (st, hid))
            if not isinstance(h.get("seq"), int) or isinstance(h.get("seq"), bool):
                errors.append("%s hypothesis %s needs an integer seq (its row in results.tsv)" % (st, hid))
        if st == "crash" and not (h.get("obstacle") or h.get("note")):
            errors.append("crash hypothesis %s needs obstacle or note (what broke)" % hid)
    return errors
