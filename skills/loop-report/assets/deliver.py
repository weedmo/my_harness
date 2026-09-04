#!/usr/bin/env python3
"""Deliver a loop-report page to where the user reads it.

    python3 deliver.py probe   --page <dir>/<slug>.html      # before the page exists is fine
    python3 deliver.py publish --page <dir>/<slug>.html [--rerun-share]
    python3 deliver.py show    --page <dir>/<slug>.html      # current state, no side effects

Routes, in order: an Orca artifact link, the Orca built-in browser tab of the
worktree, or the bare path. The route is chosen once per page and kept in
<dir>/<slug>.delivery.json, which only this script reads and writes. Every
call prints one JSON line on stdout:

    {"route": "link|tab|path", "url": ..., "browserPageId": ..., "bin": ..., "reason": ..., "page": ...}

and exits 0 whenever it answered — a run with no link is an answer, not an
error. Exit 1 only when `publish` is given a page that does not exist, or for
bad arguments. Orca command failures never raise; a transient failure keeps
the route the run already has, a denial pushes delivery down to the next
route.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

STATE_KEYS = ("route", "bin", "url", "browserPageId", "denied", "reason", "told")
NOT_FOUND_CODES = ("artifact_not_found", "not_found", "no_such_artifact", "unknown_artifact")
SHARE_DISABLED = "artifact_sharing_disabled"
AUTH_REQUIRED = "authentication_required"
TAB_NOT_FOUND = "browser_tab_not_found"
TIMEOUT = 30


def out(state, extra=None):
    d = {k: state.get(k) for k in ("route", "url", "browserPageId", "bin", "reason")}
    if extra:
        d.update(extra)
    print(json.dumps(d, ensure_ascii=False))


def fail(msg):
    print(json.dumps({"route": None, "error": msg}, ensure_ascii=False))
    sys.exit(1)


class State:
    def __init__(self, page):
        self.page = os.path.abspath(page)
        base = self.page[:-5] if self.page.endswith(".html") else self.page
        self.path = base + ".delivery.json"
        self.data = {k: None for k in STATE_KEYS}
        if os.path.isfile(self.path):
            try:
                with open(self.path, encoding="utf-8") as fh:
                    saved = json.load(fh)
                for k in STATE_KEYS:
                    if k in saved:
                        self.data[k] = saved[k]
            except (OSError, ValueError):
                pass

    def get(self, k):
        return self.data.get(k)

    def set(self, **kw):
        self.data.update(kw)

    def save(self):
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(self.data, fh, ensure_ascii=False, indent=2)
            fh.write("\n")


class Orca:
    """Thin runner around the Orca CLI; every call returns (ok, result, error_code, raw)."""

    def __init__(self, bin_name):
        self.bin = bin_name

    def run(self, *args):
        try:
            p = subprocess.run([self.bin] + list(args) + ["--json"], capture_output=True, text=True, timeout=TIMEOUT)
        except (OSError, subprocess.TimeoutExpired) as e:
            return False, None, "exec_failed", str(e)
        raw = (p.stdout or "") + (p.stderr or "")
        if "bad option: --no-sandbox" in raw:
            return False, None, "no_sandbox_shim", raw
        try:
            d = json.loads(p.stdout)
        except ValueError:
            return False, None, "not_json", raw[:200]
        if d.get("ok"):
            return True, d.get("result") or {}, None, raw
        err = d.get("error") or {}
        return False, d.get("result"), err.get("code") or "error", err.get("message") or raw[:200]


def inside_orca_terminal():
    return any(k.startswith("ORCA_") for k in os.environ)


def pick_bin(state, override=None):
    """Choose the Orca executable once. Bare `orca` outside an Orca terminal on
    Linux is usually the GNOME screen reader, so orca-ide goes first there; the
    shim's `bad option: --no-sandbox` failure is a broken shim, not a missing
    Orca, so the other binary is tried before giving up."""
    if override:
        candidates = [override]
    elif state.get("bin"):
        candidates = [state.get("bin")]
    elif inside_orca_terminal() or sys.platform != "linux":
        candidates = ["orca", "orca-ide"]
    else:
        # Outside an Orca terminal on Linux, bare `orca` is the GNOME screen
        # reader; running it starts speech on the user's machine. Never try it.
        candidates = ["orca-ide"]
    last = "orca CLI not on PATH"
    for b in candidates:
        if not shutil.which(b):
            continue
        ok, result, code, raw = Orca(b).run("status")
        if ok:
            runtime = (result or {}).get("runtime") or {}
            if runtime.get("reachable", True):
                return b, None
            last = "Orca runtime unreachable"
            continue
        last = "%s: %s" % (b, code)
    return None, last


def probe(state, override):
    b, why = pick_bin(state, override)
    if not b:
        state.set(route="path", bin=None, reason=why)
        state.save()
        return
    orca = Orca(b)
    ok, result, code, msg = orca.run("artifacts", "list")
    if ok:
        # Provisional: artifact_sharing_disabled only shows on share.
        state.set(route=state.get("route") if state.get("route") in ("link", "tab") else "link", bin=b, reason=None)
    elif code == AUTH_REQUIRED:
        state.set(route="tab", bin=b, denied=AUTH_REQUIRED, reason="Orca profile signed out (authentication_required) — browser tab instead of a link")
    else:
        state.set(route="tab", bin=b, denied=code, reason="artifacts unavailable (%s) — browser tab instead of a link" % code)
    state.save()


def try_link(state, orca, rerun_share):
    """Route 1. Returns True when the page is reachable by URL."""
    if state.get("denied") in (SHARE_DISABLED, AUTH_REQUIRED) and not rerun_share:
        state.set(reason=deny_reason(state, state.get("denied")))  # short form: already told
        return False
    if state.get("url"):
        ok, result, code, msg = orca.run("artifacts", "update", state.page)
        if ok and (result or {}).get("shareUrl"):
            state.set(route="link", url=result["shareUrl"], denied=None, reason=None)
            return True
        if code in (SHARE_DISABLED, AUTH_REQUIRED):
            state.set(denied=code, reason=deny_reason(state, code))
            return False
        if code not in NOT_FOUND_CODES:
            # A transient failure (timeout, oversize page, runtime blip): the
            # user's link still exists, so keep it and say the update did not
            # land rather than minting a second URL or demoting the run.
            state.set(route="link", reason="artifacts update failed (%s: %s) — the link is unchanged and shows the previous version; fix and publish again" % (code, str(msg)[:120]))
            return True
        # No record for this path in this profile: share afresh.
    ok, result, code, msg = orca.run("artifacts", "share", state.page)
    if ok and (result or {}).get("shareUrl"):
        state.set(route="link", url=result["shareUrl"], denied=None, reason=None)
        return True
    state.set(denied=code or "share_failed", reason=deny_reason(state, code))
    return False


def deny_reason(state, code):
    """The long explanation once (the first time this denial is seen), a short
    tag afterwards, so a loop relaying `reason` does not repeat the Settings
    instruction on every regeneration."""
    first = state.get("told") != code
    state.set(told=code)
    if code == SHARE_DISABLED:
        return ("public links are off for this device (artifact_sharing_disabled) — only a human can turn it on, in Orca desktop › Settings › Artifacts; on a headless runtime that switch may be unreachable, so the tab is the delivery for this run; pass --rerun-share only when the user says they turned it on"
                if first else "browser tab (link refused earlier: artifact_sharing_disabled)")
    if code == AUTH_REQUIRED:
        return ("Orca profile signed out (authentication_required) — browser tab instead of a link; pass --rerun-share after signing in"
                if first else "browser tab (link refused earlier: authentication_required)")
    return ("artifact link unavailable (%s) — browser tab instead" % code) if first else ("browser tab (link unavailable: %s)" % code)


def try_tab(state, orca):
    """Route 2. Open the file in the worktree's built-in browser tab, or push the
    regeneration into the tab already showing it. The built-in browser ignores
    script reloads of file:// pages, so the reload here is what makes a
    republish visible."""
    url = "file://" + state.page
    page_id = state.get("browserPageId")
    if not page_id:
        ok, result, code, msg = orca.run("tab", "list")
        if ok:
            for t in (result or {}).get("tabs") or []:
                if t.get("url") == url and t.get("browserPageId"):
                    page_id = t["browserPageId"]
                    break
    if page_id:
        ok, result, code, msg = orca.run("reload", "--page", page_id)
        if ok:
            state.set(route="tab", browserPageId=page_id, url=None)
            return True
        page_id = None  # gone (browser_tab_not_found or anything else): open a fresh one
    ok, result, code, msg = orca.run("tab", "create", "--url", url)
    if ok and (result or {}).get("browserPageId"):
        state.set(route="tab", browserPageId=result["browserPageId"], url=None)
        return True
    state.set(reason=(state.get("reason") or "") + "; tab unavailable (%s)" % code)
    return False


def publish(state, override, rerun_share):
    b, why = pick_bin(state, override)
    if not b:
        state.set(route="path", bin=None, reason=why)
        state.save()
        return
    state.set(bin=b)
    orca = Orca(b)
    tried_link = False
    if state.get("route") in (None, "link") or rerun_share:
        tried_link = True
        if try_link(state, orca, rerun_share):
            state.save()
            return
    if state.get("denied") and not tried_link:
        state.set(reason=deny_reason(state, state.get("denied")))  # already told: the short tag
    if try_tab(state, orca):
        if not state.get("reason"):
            state.set(reason="browser tab (no public link)")
        state.save()
        return
    state.set(route="path", reason=(state.get("reason") or "no link and no tab") + " — path only")
    state.save()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=("probe", "publish", "show"))
    ap.add_argument("--page", required=True, help="the rendered <slug>.html (probe/show accept a page that does not exist yet)")
    ap.add_argument("--rerun-share", action="store_true", help="retry a share the device had refused (the user says the setting changed)")
    ap.add_argument("--bin", default=os.environ.get("LOOP_REPORT_ORCA_BIN"), help="force the Orca executable")
    args = ap.parse_args()
    if args.verb == "publish" and not os.path.isfile(args.page):
        fail("page not found: " + args.page)
    state = State(args.page)
    if args.verb == "probe":
        os.makedirs(os.path.dirname(state.page), exist_ok=True)
        probe(state, args.bin)
    elif args.verb == "publish":
        publish(state, args.bin, args.rerun_share)
    out(state.data, {"page": state.page})


if __name__ == "__main__":
    main()
