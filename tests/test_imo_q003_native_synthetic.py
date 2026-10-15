#!/usr/bin/env python3
"""Native Q003 ENGINEERING smoke on fabricated data, never original/source custody.

This is deliberately not a substitute for the historical Owner-local authentic
Q003 render. All intermediate pages and receipts remain in gitignored .private.
Run only inside a full Grade9v3.5 checkout, without network access:
  python -m unittest discover -s tests -p 'test_imo_q003_native_synthetic.py' -v
"""
from __future__ import annotations

import hashlib
import importlib.util
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "TEST/imo-research/core2-q003"
STAGE = HERE / ".private"
QID = "SOF-IMO-G09-L1-2023-24-A-Q003"  # internal concept-binding key ONLY
MARKER = "SYNTHETIC TECHNICAL TEST — NOT ORIGINAL IMO Q003"
sys.path.insert(0, str(HERE))
import prepare_private as adapter  # noqa: E402
import build_private_core1a as core1a_builder  # noqa: E402


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fake_question() -> tuple[dict, dict]:
    # Deliberately fabricated numbers; the exact Q003 public source is NOT used.
    fields = ("question_id", "stem", "options", "conditions", "figures")
    row = {
        "question_id": QID, "source_url": "https://example.invalid/synthetic-never-published.pdf",
        "pdf_page_index": 0, "printed_page": 1, "printed_question_number": 3,
        "original_identifier": MARKER,
        "stem": MARKER + ". Among four INVENTED input-output observations, find a single relation for three and identify the exceptional pair.",
        "options": ["A. (1, 9)", "B. (2, 12)", "C. (3, 17)", "D. (4, 23)"],
        "conditions": [], "figures": [], "source_hints": [],
        "authored": {
            "answer": {
                "kind": "MODEL_RESPONSE",
                "summary": "Synthetic case D differs: outputs 9, 12, 17 fit y=x^2+8, but the fourth output would be 24.",
                "check": "Recompute y-x^2 on ALL four synthetic pairs to verify one mismatch.",
                "reasoning": ["Compare an invented candidate relation on every invented observation."],
                "crux_move_ref": "SYNTHETIC-MODEL-CHOICE",
                "reasoning_route": [
                    {"id": "SYNTHETIC-READ", "kind": "REPRESENT",
                     "action": "Read each fabricated pair as (input, output).",
                     "why_valid": "Consistent input/output orientation is needed.",
                     "output": "Four labelled observations."},
                    {"id": "SYNTHETIC-MODEL-CHOICE", "kind": "CONNECT",
                     "action": "Choose and test one candidate rule for every observation.",
                     "why_valid": "A common rule cannot be redefined for each option.",
                     "output": "One consistent candidate and one mismatch."},
                    {"id": "SYNTHETIC-CHECK", "kind": "VERIFY",
                     "action": "Check the same rule against the remaining observations.",
                     "why_valid": "Three agreements are the evidence for a single exception.",
                     "output": "An exception justified with an independent check."}
                ]
            },
            "scaffolds": [
                {"text": "First decide what each coordinate represents.",
                 "learner_stage": "FIRST_MOVE", "reveals": "CONCEPT"},
                {"text": "After your attempt: compare a square-plus-offset model.",
                 "learner_stage": "FORMAL_MODEL", "reveals": "METHOD"},
                {"text": "After your attempt: compute the residual of each invented pair.",
                 "learner_stage": "CHECKPOINT", "reveals": "METHOD"}
            ],
            "difficulty": {
                "band": "D2", "score": 5,
                "components": {
                    "concept_model_selection": 2, "representation_translation": 1,
                    "reasoning_chain_length": 1, "algebra_computational_load": 0,
                    "trap_exception_sensitivity": 1
                },
                "basis": "Invented test-only complexity estimate, not original Q003 QRT."
            },
            "expected_time_seconds": 90,
            "common_wrong_route": "Changing the rule between fabricated options."
        },
    }
    raw = json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    metadata = {key: row[key] for key in (
        "question_id", "source_url", "pdf_page_index",
        "printed_page", "printed_question_number"
    )}
    metadata.update({
        "private_input_sha256": hashlib.sha256(raw).hexdigest(),
        "source_item_sha256": hashlib.sha256(adapter.canonical({
            key: row[key] for key in fields
        })).hexdigest(),
        "source_document_sha256": None, "published": False,
        "verification": "SYNTHETIC_ONLY_NOT_SOURCE", "rights": "TEST_ONLY_NO_PUBLICATION",
        "qrt": "NOT_ASSESSED", "synthetic_only": True
    })
    return row, metadata


def strip_source_claims(records_file: Path, bank_file: Path) -> None:
    """Mark generated TEST pages as fabricated *before* calling the native renderer."""
    package = json.loads(records_file.read_text(encoding="utf-8"))
    for resource in package["resources"]:
        if resource["id"] == "SRC-IMO-Q003-PRIVATE":
            resource["title"] = MARKER
            resource["origin"] = "AUTHORED"
            resource["locator"] = "TEST/imo-research/core2-q003/test_imo_q003_native_synthetic.py"
            resource["access_status"] = "FULL_ITEM_INSPECTED"
            resource["rights_status"] = "TEST_ONLY_NO_PUBLISHING"
            resource["selection_reason"] = "Fabricated native smoke input; not an actual source."
    package["title"] = MARKER
    package["scope_summary"] = "SYNTHETIC ENGINEERING PAGE ONLY — not source-faithful."
    write_json(records_file, package)
    bank = json.loads(bank_file.read_text(encoding="utf-8"))
    assert len(bank["questions"]) == 1 and bank["questions"][0]["id"] == QID
    question = bank["questions"][0]
    question["origin"] = "LOCAL"  # preexisting TEST storage category, NOT canonical ORIGINAL
    question["original_identifier"] = MARKER
    ext = question["extensions"]
    ext["grade9v3:provenance_class"] = "SOURCE_UNVERIFIED"
    ext["grade9v3:analysis"]["exam_source_badge"] = MARKER
    ext["grade9v3:source_custody"] = {
        "authority_class": "SYNTHETIC_ENGINEERING_FIXTURE",
        "wording_custody": "FABRICATED_NOT_SOURCE",
        "source_status": "SYNTHETIC_NOT_VERIFIED",
        "rights_status": "TEST_ONLY_NO_PUBLICATION",
        "paper_url": None, "question_number": "3",
        "exam": "SYNTHETIC TECHNICAL TEST", "year": None, "paper": None,
    }
    write_json(bank_file, bank)


def render(manifest: Path, out: Path) -> dict:
    script = ROOT / "Shared/tools/render_core.py"
    assert script.is_file(), "Full checkout and sole renderer required"
    proc = subprocess.run(
        [sys.executable, "-I", str(script), "build", "--manifest", str(manifest),
         "--out", str(out), "--mode", "PAGES", "--draft", "--reference"],
        cwd=ROOT, capture_output=True, text=True, timeout=120
    )
    if proc.returncode:
        # Logs show exit status only, never the source item or rendered HTML.
        # Synthetic-only page: safe to report the underlying selection/contract failure.
        raise AssertionError("NATIVE_RENDER_FAILED_" + str(proc.returncode)
                             + ": " + (proc.stderr or proc.stdout)[-1700:])
    return json.loads((out / "render-receipt.json").read_text(encoding="utf-8"))


class Markers(HTMLParser):
    def __init__(self):
        super().__init__()
        self.components = set()
        self.attempts = 0
        self.commits = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "data-g9-component" in attrs:
            self.components.add(attrs["data-g9-component"])
        self.attempts += int("data-g9-attempt-box" in attrs)
        self.commits += int("data-g9-commit" in attrs)


def snapshot(path: Path) -> dict:
    raw = path.read_bytes()
    parser = Markers()
    parser.feed(raw.decode("utf-8"))
    return {
        "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
        "components": sorted(parser.components), "attempts": parser.attempts,
        "commits": parser.commits,
        "has_synthetic_marker": MARKER in raw.decode("utf-8"),
    }


@unittest.skipUnless(importlib.util.find_spec('jsonschema') is not None,
                     'native smoke requires jsonschema; run dedicated Q003 native workflow')
class Q003SyntheticNativeSmoke(unittest.TestCase):
    def test_native_core2_then_core1a_against_golden(self):
        self.assertTrue((ROOT / "Shared/tools/render_core.py").is_file(),
                        "Full repo dependencies required")
        row, receipt = fake_question()
        STAGE.mkdir(parents=True, exist_ok=True)
        source = STAGE / "q003.synthetic.private.json"
        receipt_path = STAGE / "q003.synthetic.custody.json"
        # No protected publisher data exists in this fixture, and never use
        # the frozen authentic custody-receipt.json as if these bytes matched.
        source.write_bytes(json.dumps(row, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8"))
        write_json(receipt_path, receipt)
        adapter.prepare(source, receipt_path)
        strip_source_claims(STAGE / "records.json", STAGE / "bank.json")
        core2_receipt = render(STAGE / "manifest.json", STAGE / "rendered")
        core2_page = STAGE / "rendered/core2.html"
        self.assertTrue(core2_page.exists())
        c2 = snapshot(core2_page)
        self.assertTrue(c2["has_synthetic_marker"])
        self.assertGreater(c2["attempts"], 0)
        self.assertGreater(c2["commits"], 0)
        self.assertTrue("BP-CORE2-SOURCE-QUESTION" in core2_page.read_text())
        # Native, exact registered golden; never an alternate HTML composer.
        subprocess.run([sys.executable, "-I",
                        str(ROOT / "Shared/tools/build_golden.py"),
                        "--id", "G-CORE2-R2"], cwd=ROOT, check=True,
                       capture_output=True, text=True, timeout=120)
        g2 = ROOT / "golden/units/G-CORE2-R2/rendered/core2.html"
        self.assertTrue(g2.exists())
        g2_markers = snapshot(g2)
        core1a_builder.stage_private(source, receipt_path)
        c1_root = STAGE / "core1a"
        strip_source_claims(c1_root / "records.json", c1_root / "bank.json")
        core1a_receipt = render(c1_root / "manifest.json", c1_root / "rendered")
        core1a_page = c1_root / "rendered/core1a.html"
        self.assertTrue(core1a_page.exists())
        c1 = snapshot(core1a_page)
        self.assertGreater(c1["attempts"], 0)
        self.assertGreater(c1["commits"], 0)
        self.assertTrue("BP-CORE1A-CONSTRUCTION" in core1a_page.read_text())
        subprocess.run([sys.executable, "-I",
                        str(ROOT / "Shared/tools/build_golden.py"),
                        "--id", "G-MATH-LINEAR-CONSTRAINT"], cwd=ROOT,
                       check=True, capture_output=True, text=True, timeout=120)
        g1 = ROOT / "golden/units/G-MATH-LINEAR-CONSTRAINT/rendered/core1a.html"
        self.assertTrue(g1.exists())
        g1_markers = snapshot(g1)
        # Test receipt is source-safe and ignored; zero depth gaps is NOT
        # assumed: enumerate them and leave any genuinely missing duties open.
        write_json(STAGE / "q003.synthetic.native-receipt.json", {
            "scope": "SYNTHETIC_NATIVE_TECHNICAL_ONLY",
            "real_q003_original_used": False,
            "academic_qrt_accepted": False, "publication": False,
            "core2": c2, "core1a": c1,
            "core2_golden": g2_markers, "core1a_golden": g1_markers,
            "gap_counts": {
                "core2": len(core2_receipt.get("gaps") or []),
                "core1a": len(core1a_receipt.get("gaps") or [])
            },
            "gap_duties": {
                "core2": sorted({g["duty"] for g in core2_receipt.get("gaps") or []}),
                "core1a": sorted({g["duty"] for g in core1a_receipt.get("gaps") or []})
            }
        })
        print("SYNTHETIC Q003 native Core2/Golden/Core1A/Golden complete;"
              " all pages remain ignored and unreleased")
        print("Core2 gaps:", len(core2_receipt.get("gaps") or []),
              "duties:", sorted({g["duty"] for g in core2_receipt.get("gaps") or []}),
              "Core1A gaps:", len(core1a_receipt.get("gaps") or []),
              "duties:", sorted({g["duty"] for g in core1a_receipt.get("gaps") or []}))
        print("Synthetic Core2 exact gap findings:",
              [(g.get("duty"), g.get("component"), g.get("detail"))
               for g in core2_receipt.get("gaps") or []])
        print("Core2 missing golden slots:", sorted(set(g2_markers["components"]) - set(c2["components"])))
        print("Core1A missing golden slots:", sorted(set(g1_markers["components"]) - set(c1["components"])))


if __name__ == "__main__":
    unittest.main()
