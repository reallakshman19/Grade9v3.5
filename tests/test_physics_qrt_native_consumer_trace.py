"""Read-only native source->selection->render evidence check with falsifiers."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from Physics.adapter.qrt_program.qrt_native_consumer_trace import (
    trace, inspect_rendered_html, QUESTION_ID, SOURCE, MANIFEST, GOLDEN,
)


class NativeConsumerProbeTests(unittest.TestCase):
    def test_actual_source_manifest_and_candidate_golden_are_bound(self):
        report = trace()
        rows = {x["join"]: x for x in report["checks"]}
        self.assertEqual(rows["CANONICAL_SOURCE"]["status"], "PASS")
        self.assertEqual(rows["PRODUCT_SELECTION"]["status"], "PASS")
        self.assertEqual(rows["GOLDEN_SELECTION_CANDIDATE"]["status"], "PASS")
        self.assertEqual(report["first_unproven_join"], "NATIVE_IN_MEMORY_RENDER")
        self.assertEqual(report["browser_verdict"], "NOT_RUN")
        self.assertEqual(report["release_verdict"], "HOLD")

    def test_inert_answer_does_not_count_as_initial_text(self):
        move = "Only the 37 degree pull starts the crate."
        html = (f'<article data-g9-unit="{QUESTION_ID}" data-g9-role="CORE2B">'
                '<div data-g9-attempt-box><button data-g9-commit>Commit</button></div>'
                '<details data-requires-attempt><summary>Review</summary></details>'
                f'<template data-g9-payload="p"><p>{move}</p></template></article>')
        observed = inspect_rendered_html(html, QUESTION_ID, move)
        self.assertEqual(observed["status"], "STATIC_STRUCTURE_OBSERVED")
        self.assertTrue(observed["protected_move_in_template"])
        self.assertFalse(observed["protected_move_in_initial_article_text"])
        self.assertEqual(observed["javascript_enforced"], "NOT_RUN")

    def test_falsifier_for_visible_answer(self):
        move = "Decide 37 degree"
        html = (f'<article data-g9-unit="{QUESTION_ID}" data-g9-role="CORE2B">'
                f'<p>{move}</p><div data-g9-attempt-box><button data-g9-commit>Commit</button></div>'
                '<details data-requires-attempt></details>'
                f'<template data-g9-payload="p"><p>{move}</p></template></article>')
        self.assertIn("PROTECTED_MOVE_IN_INITIAL_ARTICLE_TEXT",
                      inspect_rendered_html(html, QUESTION_ID, move)["problems"])

    def test_false_source_candidate_cardinality(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = root / SOURCE
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"questions": []}), encoding="utf-8")
            packet = trace(root=root)
            self.assertEqual(packet["first_unproven_join"], "CANONICAL_SOURCE")
            self.assertEqual(packet["checks"][0]["status"], "FAIL")

    def test_missing_selected_prerequisite_is_not_proven(self):
        repo = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for name in (SOURCE, MANIFEST, GOLDEN):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((repo / name).read_bytes())
            selection = root / MANIFEST
            data = json.loads(selection.read_text())
            data["selection"]["core2a"] = []
            selection.write_text(json.dumps(data))
            result = trace(root=root)
            self.assertEqual(result["first_unproven_join"], "PRODUCT_SELECTION")
            self.assertEqual(result["publication_verdict"], "NOT_ATTESTED")

    def test_uncommitted_published_page_is_not_inferred_from_manifest(self):
        report = trace()
        rows = {x["join"]: x for x in report["checks"]}
        self.assertNotEqual(rows["OWNER_ACCEPTED_PUBLIC_RENDER"]["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
