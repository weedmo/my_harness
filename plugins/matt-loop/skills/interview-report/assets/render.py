#!/usr/bin/env python3
"""Render the decision-graph HTML from template.html plus a data JSON file.

    python3 render.py --data docs/agents/matt-auto-log/<slug>.data.json \
                      --out  docs/agents/matt-auto-log/<slug>.html

The template is never edited by hand: only the <title> and the
<script id="graph-data"> block change, and this script is the only thing
that changes them. It validates the data first and refuses to write a page
that would render wrong, so a regeneration either succeeds whole or fails
loudly.
"""
import argparse
import json
import os
import re
import sys

TITLE_RE = re.compile(r"^<title>.*?</title>$", re.M)
DATA_RE = re.compile(
    r'^<script id="graph-data" type="application/json">\n.*?\n</script>$', re.M | re.S
)
PROGRESS_STATES = {"running", "blocked", "done"}
TICKET_STATUSES = {"pending", "in-progress", "done", "blocked", "skipped"}
FILE_STATUSES = {"added", "modified", "deleted", "renamed"}
FILE_KINDS = {"code", "docs", "other"}


def fail(msg):
    sys.stderr.write("render.py: " + msg + "\n")
    sys.exit(1)


def validate(d):
    errors = []
    for key in ("title", "slug", "generated", "summary", "stages"):
        if key not in d:
            errors.append("missing top-level key: " + key)
    if errors:
        return errors
    seen = set()
    for st in d["stages"]:
        for key in ("id", "name", "status"):
            if key not in st:
                errors.append("stage without " + key + ": " + json.dumps(st, ensure_ascii=False)[:80])
        for dec in st.get("decisions", []):
            for key in ("id", "question", "decision", "rationale"):
                if key not in dec:
                    errors.append("decision without " + key + ": " + json.dumps(dec, ensure_ascii=False)[:80])
            if dec.get("id") in seen:
                errors.append("duplicate decision id: " + str(dec.get("id")))
            seen.add(dec.get("id"))
    pr = d.get("progress")
    if pr is not None:
        if pr.get("state") not in PROGRESS_STATES:
            errors.append("progress.state must be one of " + ", ".join(sorted(PROGRESS_STATES)))
        if "updated" not in pr:
            errors.append("progress.updated is required (ISO timestamp from the clock)")
    for tk in d.get("tickets", []):
        if tk.get("status") not in TICKET_STATUSES:
            errors.append("ticket %s has unknown status %r" % (tk.get("id"), tk.get("status")))
        if tk.get("status") == "blocked":
            b = tk.get("blocker") or {}
            if not b.get("reason") or not b.get("detail"):
                errors.append("blocked ticket %s needs blocker.reason and blocker.detail" % tk.get("id"))
    out = d.get("outcome")
    if out is not None:
        for f in out.get("files", []):
            if f.get("status") not in FILE_STATUSES or f.get("kind") not in FILE_KINDS:
                errors.append("outcome file %s needs status in %s and kind in %s"
                              % (f.get("path"), sorted(FILE_STATUSES), sorted(FILE_KINDS)))
            if not isinstance(f.get("added"), int) or not isinstance(f.get("removed"), int):
                errors.append("outcome file %s needs integer added/removed from git diff --numstat" % f.get("path"))
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="path to <slug>.data.json")
    ap.add_argument("--out", required=True, help="path to <slug>.html to write")
    ap.add_argument("--template", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.html"))
    args = ap.parse_args()

    try:
        with open(args.data, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as e:
        fail("cannot read data: %s" % e)
    errors = validate(data)
    if errors:
        fail("data is not renderable:\n  - " + "\n  - ".join(errors))

    try:
        with open(args.template, encoding="utf-8") as fh:
            tpl = fh.read()
    except OSError as e:
        fail("cannot read template: %s" % e)
    if not TITLE_RE.search(tpl) or not DATA_RE.search(tpl):
        fail("template has no <title> / graph-data block at column 0 — wrong file?")

    block = '<script id="graph-data" type="application/json">\n' \
        + json.dumps(data, ensure_ascii=False, indent=1) + "\n</script>"
    html = TITLE_RE.sub(lambda _: "<title>" + data["title"] + " — 결정 그래프</title>", tpl, count=1)
    html = DATA_RE.sub(lambda _: block, html, count=1)

    # The only allowed difference from the template is the two replaced spans.
    if "function startPolling" not in html or len(html) < len(tpl) - 4000:
        fail("output lost template machinery — refusing to write")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(html)
    decisions = sum(len(s.get("decisions", [])) for s in data["stages"])
    state = (data.get("progress") or {}).get("state", "gate")
    print("wrote %s (%d bytes, %d decisions, state=%s)" % (args.out, len(html.encode("utf-8")), decisions, state))


if __name__ == "__main__":
    main()
