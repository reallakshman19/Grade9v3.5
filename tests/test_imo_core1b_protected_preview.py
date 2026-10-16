"""Core1B TEST source boundary: do not serialize protected reasoning."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "TEST/imo-research/build_core1b_protected_preview.py"
spec = importlib.util.spec_from_file_location("core1b_review_generator", SRC)
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)

class Core1BHeldPreviewTests(unittest.TestCase):
    def test_generator_output_is_exact_and_answer_free(self):
        rendered = generator.build()
        self.assertEqual(rendered, generator.OUTPUT.read_bytes())
        html = rendered.decode("utf-8")
        for marker in (
            'data-g9-preview-core="CORE1B"',
            'data-g9-canonical-acceptance="false"',
            'data-g9-proof-custody="WITHHELD"',
            "if(!field.value.trim())",
            "Blank attempts are refused",
        ):
            self.assertIn(marker, html)
        for unsafe in ("<template", "data-g9-payload", "data-g9-solution",
                       "application/json", "data-g9-independent"):
            self.assertNotIn(unsafe, html)
        source = json.loads(generator.SOURCE.read_text(encoding="utf-8"))
        for micro in source["microtopics"]:
            lines = [micro["inferential_jump"]]
            lines.extend(step["why_valid"] for step in micro["teaching_path"])
            answer = micro.get("exit_task", {}).get("answer") or {}
            lines.extend(str(value) for value in answer.values())
            for line in lines:
                if isinstance(line, str) and len(line) >= 32:
                    self.assertNotIn(line, html)

    def test_no_source_repin_or_academic_grant_by_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wrong-source.json"
            data = json.loads(generator.SOURCE.read_text(encoding="utf-8"))
            data["extensions"]["grade9v3:learner_published"] = True
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "CORE1B_SOURCE_BLOB_DRIFT"):
                generator.build(path)

    def test_docs_mirror_is_a_separate_generator_lane(self):
        self.assertEqual(generator.OUTPUT.relative_to(REPO).as_posix(),
                         "public/test/imo-grade9/core1b.html")
        self.assertNotIn("docs/test/imo-grade9/", generator.HTML)

if __name__ == "__main__":
    unittest.main()
