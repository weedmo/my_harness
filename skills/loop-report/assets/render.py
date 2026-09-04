#!/usr/bin/env python3
"""Render a loop-report page from shell.html + a view + a data JSON file.

    python3 render.py --data <slug>.data.json --out <slug>.html \
                      [--view <plugin>/assets/view.html]

The shell is never edited by hand: this script swaps in the <title>, the
view's <style> and <script> fragments, and the <script id="graph-data">
block, and nothing else. It validates the common data contract first, then
the view's own contract when a validate.py sits next to the view, and
refuses to write a page that would render wrong — a regeneration either
succeeds whole or fails loudly.
"""
import argparse
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TITLE_RE = re.compile(r"^<title>.*?</title>$", re.M)
DATA_RE = re.compile(
    r'^<script id="graph-data" type="application/json">\n.*?\n</script>$', re.M | re.S
)
VIEW_STYLE_MARK = "<!-- view:style -->"
VIEW_SCRIPT_MARK = "<!-- view:script -->"
# Tags at column 0 only, so prose in the view's header comment cannot match.
STYLE_RE = re.compile(r"^<style>$.*?^</style>$", re.S | re.M)
SCRIPT_RE = re.compile(r"^<script>$.*?^</script>$", re.S | re.M)

PROGRESS_STATES = {"running", "blocked", "done"}
FILE_STATUSES = {"added", "modified", "deleted", "renamed"}
FILE_KINDS = {"code", "docs", "other"}


def fail(msg):
    sys.stderr.write("render.py: " + msg + "\n")
    sys.exit(1)


def validate_common(d):
    errors = []
    for key in ("title", "slug", "generated", "summary"):
        if key not in d:
            errors.append("missing top-level key: " + key)
    pr = d.get("progress")
    if pr is not None:
        if pr.get("state") not in PROGRESS_STATES:
            errors.append("progress.state must be one of " + ", ".join(sorted(PROGRESS_STATES)))
        if "updated" not in pr:
            errors.append("progress.updated is required (ISO timestamp from the clock)")
        for b in pr.get("blockers", []) or []:
            if not b.get("title") or not b.get("detail"):
                errors.append("progress.blockers entries need title and detail (the checkable fact)")
    out = d.get("outcome")
    if out is not None:
        # The final regeneration: the header must say 완료, otherwise the page
        # keeps polling and the run looks unfinished.
        if not pr or pr.get("state") != "done":
            errors.append("outcome present but progress.state is not \"done\" — the final regeneration needs progress")
        for f in out.get("files", []) or []:
            if f.get("status") not in FILE_STATUSES or f.get("kind") not in FILE_KINDS:
                errors.append("outcome file %s needs status in %s and kind in %s"
                              % (f.get("path"), sorted(FILE_STATUSES), sorted(FILE_KINDS)))
            if not isinstance(f.get("added"), int) or not isinstance(f.get("removed"), int):
                errors.append("outcome file %s needs integer added/removed from git diff --numstat" % f.get("path"))
    return errors


def load_view_validator(view_path):
    """validate.py next to the view exposes validate(data) -> [error, ...]."""
    if not view_path:
        return None
    candidate = os.path.join(os.path.dirname(os.path.abspath(view_path)), "validate.py")
    if not os.path.isfile(candidate):
        return None
    spec = importlib.util.spec_from_file_location("loop_report_view_validate", candidate)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "validate"):
        fail("%s has no validate(data) function" % candidate)
    return mod.validate


def read(path, what):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError as e:
        fail("cannot read %s: %s" % (what, e))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="path to <slug>.data.json")
    ap.add_argument("--out", required=True, help="path to <slug>.html to write")
    ap.add_argument("--view", default=None, help="the loop's view.html (omit for the bare shell)")
    ap.add_argument("--shell", default=os.path.join(HERE, "shell.html"))
    args = ap.parse_args()

    try:
        data = json.loads(read(args.data, "data"))
    except ValueError as e:
        fail("cannot parse data: %s" % e)
    errors = validate_common(data)
    view_validate = load_view_validator(args.view)
    if view_validate and not errors:
        errors = list(view_validate(data) or [])
    if errors:
        fail("data is not renderable:\n  - " + "\n  - ".join(errors))

    shell = read(args.shell, "shell")
    if not TITLE_RE.search(shell) or not DATA_RE.search(shell):
        fail("shell has no <title> / graph-data block at column 0 — wrong file?")
    if VIEW_STYLE_MARK not in shell or VIEW_SCRIPT_MARK not in shell:
        fail("shell has no view markers — wrong file?")

    view_style, view_script = "", ""
    if args.view:
        view = read(args.view, "view")
        m_style = STYLE_RE.search(view)
        m_script = SCRIPT_RE.search(view)
        if not m_script or "window.LoopView" not in m_script.group(0):
            fail("view has no <script> registering window.LoopView — wrong file?")
        view_style = m_style.group(0) if m_style else ""
        view_script = m_script.group(0)

    block = '<script id="graph-data" type="application/json">\n' \
        + json.dumps(data, ensure_ascii=False, indent=1) + "\n</script>"
    html = TITLE_RE.sub(lambda _: "<title>" + data["title"] + "</title>", shell, count=1)
    html = DATA_RE.sub(lambda _: block, html, count=1)
    html = html.replace(VIEW_STYLE_MARK, view_style, 1)
    html = html.replace(VIEW_SCRIPT_MARK, view_script, 1)

    # The only allowed differences from the shell are the spliced spans.
    expected_min = len(shell) + len(view_style) + len(view_script) - 4000
    if "function startPolling" not in html or len(html) < expected_min:
        fail("output lost shell machinery — refusing to write")
    if args.view and "window.LoopView" not in html:
        fail("output lost the view — refusing to write")

    out_dir = os.path.dirname(os.path.abspath(args.out))
    os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(html)
    state = (data.get("progress") or {}).get("state", "gate")
    print("wrote %s (%d bytes, view=%s, state=%s)"
          % (args.out, len(html.encode("utf-8")), os.path.basename(args.view) if args.view else "none", state))


if __name__ == "__main__":
    main()
