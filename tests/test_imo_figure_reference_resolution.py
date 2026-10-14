#!/usr/bin/env python3
"""Source-safe figure-reference regression for the isolated PR #240 repair.

This test reads only repository question IDs and figure_ref paths, not original
question stems, choices, answers, or publisher image contents for assertion.
It is independent of the standalone suite's generation side effects.

Run: python -m unittest -v tests.test_imo_figure_reference_resolution
"""
from __future__ import annotations

import ast
from contextlib import contextmanager
import html
import json
import os
from pathlib import Path
import re
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "Mathematics" / "research" / "build_full_master_suite.py"
BANKS = ROOT / "Mathematics" / "question-bank"


def load_figure_function():
    # Compile just the exact committed function. Do not execute the builder
    # module or generate public original-question HTML.
    tree = ast.parse(BUILDER.read_text(encoding="utf-8"), filename=str(BUILDER))
    nodes = [node for node in tree.body
             if isinstance(node, ast.FunctionDef) and node.name == "get_figure_markup"]
    if len(nodes) != 1:
        raise AssertionError("UNIQUE_FIGURE_FUNCTION_REQUIRED")
    unit = ast.Module(body=nodes, type_ignores=[])
    scope = {"Path": Path, "re": re, "html": html}
    exec(compile(unit, str(BUILDER), "exec"), scope)
    return scope["get_figure_markup"]


@contextmanager
def working_directory(path: Path):
    prior = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prior)


def declared_refs():
    refs = []
    for bank in sorted(BANKS.glob("*.core2.json")):
        data = json.loads(bank.read_text(encoding="utf-8"))
        for question in data["questions"]:
            if question.get("figure_ref"):
                refs.append((question["id"], question["figure_ref"]))
    return refs


class FigureReferenceRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.render = staticmethod(load_figure_function())

    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.library = self.root / "Mathematics" / "library" / "figures"
        self.library.mkdir(parents=True, exist_ok=True)
        self.asset = self.library / "created-by-test.svg"
        self.asset.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>',
                              encoding="utf-8")

    def render_here(self, ref, qid="AUTHORED-FIGURE-TEST"):
        with working_directory(self.root):
            return self.render(ref, qid)

    def test_all_declared_bank_figures_resolve_at_repository_root(self):
        refs = declared_refs()
        self.assertGreaterEqual(len(refs), 32, "COVERAGE_REGRESSION")
        self.assertEqual(len(refs), len(set(qid for qid, _ in refs)))
        with working_directory(ROOT):
            for qid, ref in refs:
                with self.subTest(qid=qid):
                    result = self.render(ref, qid)
                    self.assertIn("<svg", result, "DECLARED_FIGURE_NOT_RENDERED")

    def test_both_supported_reference_forms(self):
        for ref in (
            "created-by-test.svg",
            "Mathematics/library/figures/created-by-test.svg",
        ):
            with self.subTest(ref=ref):
                self.assertIn("<svg", self.render_here(ref))

    def test_missing_declared_reference_fails_closed(self):
        with self.assertRaisesRegex(FileNotFoundError, "DECLARED_FIGURE_MISSING"):
            self.render_here("absent.svg")

    def test_absolute_reference_rejected(self):
        with self.assertRaisesRegex(ValueError, "UNSAFE_FIGURE_REFERENCE"):
            self.render_here("/tmp/elsewhere.svg")

    def test_parent_traversal_rejected(self):
        with self.assertRaisesRegex(ValueError, "UNSAFE_FIGURE_REFERENCE"):
            self.render_here("../outside.svg")

    def test_nested_unknown_directory_rejected(self):
        with self.assertRaisesRegex(ValueError, "FIGURE_NOT_IN_LIBRARY_FLAT_NAMESPACE"):
            self.render_here("other/created-by-test.svg")

    def test_non_svg_reference_rejected(self):
        with self.assertRaisesRegex(ValueError, "UNSAFE_FIGURE_REFERENCE"):
            self.render_here("script.js")

    def test_symlink_escape_rejected(self):
        outside = self.root / "outside.svg"
        outside.write_text("<svg/>", encoding="utf-8")
        try:
            (self.library / "alias.svg").symlink_to(outside)
        except OSError:
            self.skipTest("symlink unsupported on this test host")
        with self.assertRaisesRegex(ValueError, "FIGURE_ESCAPES_LIBRARY"):
            self.render_here("alias.svg")

    def test_no_declared_figure_falls_back_safely(self):
        self.assertEqual(self.render_here(None), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
