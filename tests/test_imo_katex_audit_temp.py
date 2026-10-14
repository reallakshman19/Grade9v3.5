"""No publisher content: synthetic regression for issue #257's KaTeX audit isolation."""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from Shared.tools import audit_math_and_fonts as auditor


class TemporaryKatexAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="imo257-fixture-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.vendor = self.root / "standalone/vendor/katex/0.16.8/katex.min.js"
        self.vendor.parent.mkdir(parents=True)
        self.vendor.write_text(
            """
            module.exports = {renderToString: function(inner, options) {
                if (inner.includes("INVALID")) return '<span class="katex-error">bad math</span>';
                if (inner === "inline" && options.displayMode) return '<span class="katex-error">inline wrongly displayed</span>';
                if (inner === "display" && !options.displayMode) return '<span class="katex-error">display wrongly inline</span>';
                return '<span class="katex">valid</span>';
            }};
            """,
            encoding="utf-8",
        )
        self.page = self.root / "synthetic.html"
        self.mock_root = mock.patch.object(auditor, "REPO_ROOT", self.root)
        self.mock_root.start()
        self.addCleanup(self.mock_root.stop)
        self.assertFalse((self.root / "scratch").exists(), "fixture must begin with no scratch directory")

    def _audit(self, content="$2+2=4$"):
        self.page.write_text("<!doctype html><html><body>" + content + "</body></html>", encoding="utf-8")
        return auditor.audit_html_file(self.page)

    @unittest.skipUnless(shutil.which("node"), "Node.js required for actual stub-runtime integration")
    def test_clean_checkout_runs_without_creating_repo_scratch(self):
        self.assertEqual(self._audit("$2+2=4$"), [])
        self.assertFalse((self.root / "scratch").exists())

    @unittest.skipUnless(shutil.which("node"), "Node.js required for actual stub-runtime integration")
    def test_inline_and_display_math_modes_are_distinct(self):
        self.assertEqual(self._audit("$inline$ and $$display$$"), [])

    @unittest.skipUnless(shutil.which("node"), "Node.js required for actual stub-runtime integration")
    def test_invalid_synthetic_math_blocks_release(self):
        found = self._audit("$INVALID$")
        self.assertEqual([f["rule"] for f in found], ["MATH_SYNTAX_VALID"])
        self.assertTrue(all(f["severity"] == "BLOCK" for f in found))
        self.assertFalse((self.root / "scratch").exists())

    def test_auditor_does_not_leak_ephemeral_json_or_scripts(self):
        captured = []
        def fake_run(args, **kwargs):
            script = Path(args[1])
            captured.append(script.parent)
            self.assertTrue(script.is_file())
            self.assertTrue((script.parent / "_katex_input.json").is_file())
            items = json.loads((script.parent / "_katex_input.json").read_text(encoding="utf-8"))
            self.assertEqual(items[0]["inner"], "2+2=4")
            return subprocess.CompletedProcess(args=args, returncode=0, stdout="[]", stderr="")
        with mock.patch.object(auditor.subprocess, "run", side_effect=fake_run):
            self.assertEqual(self._audit(), [])
            self.assertEqual(self._audit(), [])
        self.assertEqual(len(captured), 2)
        self.assertNotEqual(captured[0], captured[1], "each run must have a distinct temp workspace")
        self.assertTrue(all(not d.exists() for d in captured))
        self.assertFalse((self.root / "scratch").exists())

    def test_node_unavailable_is_a_blocking_finding_not_a_false_pass(self):
        with mock.patch.object(auditor.subprocess, "run", side_effect=FileNotFoundError("node unavailable")):
            found = self._audit()
        self.assertEqual([f["rule"] for f in found], ["MATH_SYNTAX_VALIDATOR_ERROR"])
        self.assertIn("could not run", found[0]["detail"])
        self.assertFalse((self.root / "scratch").exists())

    def test_node_nonzero_exit_is_a_blocking_finding(self):
        result = subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr="deliberate runtime error")
        with mock.patch.object(auditor.subprocess, "run", return_value=result):
            found = self._audit()
        self.assertEqual([f["rule"] for f in found], ["MATH_SYNTAX_VALIDATOR_ERROR"])
        self.assertIn("deliberate runtime error", found[0]["detail"])

    def test_invalid_node_payload_is_a_blocking_finding(self):
        result = subprocess.CompletedProcess(args=[], returncode=0, stdout="not json", stderr="")
        with mock.patch.object(auditor.subprocess, "run", return_value=result):
            found = self._audit()
        self.assertEqual([f["rule"] for f in found], ["MATH_SYNTAX_VALIDATOR_ERROR"])
        self.assertIn("output invalid", found[0]["detail"])

    def test_font_floor_is_still_a_blocking_rule(self):
        result = subprocess.CompletedProcess(args=[], returncode=0, stdout="[]", stderr="")
        with mock.patch.object(auditor.subprocess, "run", return_value=result):
            found = self._audit("$2+2=4$ <div style='font-size: 10px'>synthetic</div>")
        self.assertIn("FONT_FLOOR_RIGOR", [f["rule"] for f in found])


if __name__ == "__main__":
    unittest.main()
