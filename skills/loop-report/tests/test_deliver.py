"""deliver.py against the fake Orca CLI next to this file. No real Orca needed:

    python3 -m unittest skills/loop-report/tests/test_deliver.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DELIVER = os.path.join(HERE, "..", "assets", "deliver.py")
FAKE = os.path.join(HERE, "fake-orca-ide")


class DeliverTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.bindir = os.path.join(self.tmp, "bin")
        os.makedirs(self.bindir)
        shutil.copy(FAKE, os.path.join(self.bindir, "orca-ide"))
        os.chmod(os.path.join(self.bindir, "orca-ide"), 0o755)
        # A PATH with only what the fake needs, so the real system `orca`
        # (the GNOME screen reader on Linux) can never be picked up.
        self.tools = os.path.join(self.tmp, "tools")
        os.makedirs(self.tools)
        for tool in ("bash", "env", "printf"):
            real = shutil.which(tool)
            if real:
                os.symlink(real, os.path.join(self.tools, tool))
        self.page = os.path.join(self.tmp, "run.html")
        with open(self.page, "w") as fh:
            fh.write("<html></html>")
        self.log = os.path.join(self.tmp, "calls.log")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_deliver(self, verb, scenario="link", extra=(), env=None, with_bin=True):
        e = {k: v for k, v in os.environ.items() if not k.startswith("ORCA_") and k != "LOOP_REPORT_ORCA_BIN"}
        e["PATH"] = (self.bindir + os.pathsep if with_bin else "") + self.tools
        e["FAKE_ORCA_SCENARIO"] = scenario
        e["FAKE_ORCA_LOG"] = self.log
        e.update(env or {})
        p = subprocess.run([sys.executable, DELIVER, verb, "--page", self.page] + list(extra),
                           capture_output=True, text=True, env=e)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        return json.loads(p.stdout.strip().splitlines()[-1])

    def calls(self):
        with open(self.log) as fh:
            return [l.strip() for l in fh if l.strip()]

    def state(self):
        with open(self.page[:-5] + ".delivery.json") as fh:
            return json.load(fh)

    def test_probe_link(self):
        r = self.run_deliver("probe")
        self.assertEqual(r["route"], "link")
        self.assertEqual(r["bin"], "orca-ide")

    def test_probe_auth_required_means_tab(self):
        r = self.run_deliver("probe", "auth")
        self.assertEqual(r["route"], "tab")
        self.assertIn("authentication_required", r["reason"])

    def test_probe_without_orca_is_path(self):
        r = self.run_deliver("probe", with_bin=False)
        self.assertEqual(r["route"], "path")
        self.assertIsNone(r["bin"])

    def test_publish_link_then_update_keeps_url(self):
        first = self.run_deliver("publish")
        self.assertEqual(first["route"], "link")
        self.assertTrue(first["url"].startswith("https://"))
        second = self.run_deliver("publish")
        self.assertEqual(second["url"], first["url"].replace("share-1", "update-1"))
        c = self.calls()
        self.assertIn("artifacts share " + self.page + " --json", c)
        self.assertIn("artifacts update " + self.page + " --json", c)

    def test_publish_update_without_record_falls_back_to_share(self):
        self.run_deliver("publish")
        r = self.run_deliver("publish", env={"FAKE_ORCA_NO_RECORD": "1"})
        self.assertEqual(r["route"], "link")
        self.assertEqual(self.calls().count("artifacts share " + self.page + " --json"), 2)

    def test_share_disabled_drops_to_tab_and_never_retries(self):
        r1 = self.run_deliver("publish", "disabled")
        self.assertEqual(r1["route"], "tab")
        self.assertEqual(r1["browserPageId"], "page-new")
        self.assertIn("artifact_sharing_disabled", r1["reason"])
        r2 = self.run_deliver("publish", "disabled")
        self.assertEqual(r2["browserPageId"], "page-new")
        c = self.calls()
        self.assertEqual(sum(1 for x in c if x.startswith("artifacts share")), 1)
        self.assertEqual(sum(1 for x in c if x.startswith("reload --page page-new")), 1)
        self.assertEqual(sum(1 for x in c if x.startswith("tab create")), 1)

    def test_rerun_share_retries_once_the_user_says_so(self):
        self.run_deliver("publish", "disabled")
        r = self.run_deliver("publish", "link", extra=["--rerun-share"])
        self.assertEqual(r["route"], "link")
        self.assertEqual(self.state()["denied"], None)

    def test_existing_tab_is_reused(self):
        r = self.run_deliver("publish", "auth", env={"FAKE_ORCA_EXISTING_TAB": "file://" + self.page})
        self.assertEqual(r["route"], "tab")
        self.assertEqual(r["browserPageId"], "page-existing")
        self.assertFalse(any(x.startswith("tab create") for x in self.calls()))

    def test_gone_tab_is_recreated(self):
        self.run_deliver("publish", "auth")
        r = self.run_deliver("publish", "auth", env={"FAKE_ORCA_TAB_GONE": "1"})
        self.assertEqual(r["route"], "tab")
        self.assertEqual(r["browserPageId"], "page-new")
        self.assertEqual(sum(1 for x in self.calls() if x.startswith("tab create")), 2)

    def test_no_link_no_tab_is_path(self):
        r = self.run_deliver("publish", "notab")
        self.assertEqual(r["route"], "path")
        self.assertIn("path only", r["reason"])

    def test_broken_shim_falls_through_to_next_bin(self):
        # Only a shim-like binary is available and it fails: no Orca, path route, exit 0.
        r = self.run_deliver("publish", "shim")
        self.assertEqual(r["route"], "path")
        self.assertIn("no_sandbox_shim", r["reason"])

    def test_probe_before_the_page_exists(self):
        os.remove(self.page)
        r = self.run_deliver("probe")
        self.assertEqual(r["route"], "link")
        self.assertTrue(os.path.isfile(self.page[:-5] + ".delivery.json"))

    def test_show_reports_state_without_side_effects(self):
        self.run_deliver("publish", "auth")
        before = self.calls()
        r = self.run_deliver("show", "auth")
        self.assertEqual(r["route"], "tab")
        self.assertEqual(r["browserPageId"], "page-new")
        self.assertEqual(self.calls(), before)

    def test_transient_update_failure_keeps_the_link(self):
        first = self.run_deliver("publish")
        r = self.run_deliver("publish", env={"FAKE_ORCA_UPDATE_FAIL": "timeout"})
        self.assertEqual(r["route"], "link")
        self.assertEqual(r["url"], first["url"])
        self.assertIn("update failed", r["reason"])
        self.assertEqual(sum(1 for x in self.calls() if x.startswith("artifacts share")), 1)
        again = self.run_deliver("publish")
        self.assertEqual(again["route"], "link")
        self.assertIsNone(again["reason"])

    def test_denial_reason_is_long_once_then_short(self):
        r1 = self.run_deliver("publish", "disabled")
        r2 = self.run_deliver("publish", "disabled")
        self.assertIn("Settings", r1["reason"])
        self.assertNotIn("Settings", r2["reason"])
        self.assertIn("artifact_sharing_disabled", r2["reason"])

    def test_missing_page_exits_1(self):
        p = subprocess.run([sys.executable, DELIVER, "publish", "--page", os.path.join(self.tmp, "nope.html")],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 1)


if __name__ == "__main__":
    unittest.main()
