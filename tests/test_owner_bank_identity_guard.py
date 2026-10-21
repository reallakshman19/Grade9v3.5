"""Synthetic source-occurrence bijection checks; no private Owner-bank or Physics data."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from Shared.tools import owner_bank
from Shared.tools import web_blueprint_contract as blueprints

IDENTITY = ("INTAKE_ID_", "INTAKE_REF_", "ALIAS_COLLISION", "CARDINALITY_MISMATCH",
            "intake question ", "not a question id in the intake", "not the intake's text")


def intake(*ids_and_text):
    return {"status": "RESEARCH_AND_AUTHOR", "errors": [], "intake_digest": "sha256:synthetic-intake",
            "inputs": {"questions": [{"id": key, "label": str(index), "text": value}
                                      for index, (key, value) in enumerate(ids_and_text, 1)]}}


def identity_errors(problems):
    return [message for message in problems if any(marker in message for marker in IDENTITY)]


class OwnerBankIdentityGuard(unittest.TestCase):
    def setUp(self):
        self.source = intake(("q1", "Invented: add 2 and 3."), ("q2", "Invented: add 4 and 5."))
        self.bank = owner_bank.new(self.source, "synthetic")
        self.custody = owner_bank.CUSTODY_KEY

    def check(self, source=True):
        return owner_bank.check(self.bank, intake=self.source if source else None, complete=False)

    def test_t1_t6_unique_source_and_normal_sequence(self):
        self.assertEqual([q["id"] for q in self.bank["questions"]],
                         ["OWN-SYNTHETIC-01", "OWN-SYNTHETIC-02"])
        self.assertEqual([q["original_identifier"] for q in self.bank["questions"]], ["Q1", "Q2"])
        self.assertEqual([q["stem"] for q in self.bank["questions"]],
                         [q["text"] for q in self.source["inputs"]["questions"]])
        self.assertEqual(identity_errors(self.check()), [])
        self.assertTrue(self.check(), "draft authoring gaps are preserved")
        self.assertEqual(self.bank["questions"][0]["extensions"][self.custody]["text_sha256"],
                         owner_bank.text_digest("Invented: add 2 and 3."))

    def test_t2_collision_same_text_negative_mutant(self):
        self.source["inputs"]["questions"][1] = copy.deepcopy(self.source["inputs"]["questions"][0])
        with self.assertRaisesRegex(ValueError, "INTAKE_ID_COLLISION"):
            owner_bank.new(self.source, "synthetic")
        self.assertIn("INTAKE_ID_COLLISION", " ".join(self.check()))
        
    def test_t3_collision_different_text_negative_mutant(self):
        self.source["inputs"]["questions"][1]["id"] = "q1"
        with self.assertRaisesRegex(ValueError, "INTAKE_ID_COLLISION"):
            owner_bank.new(self.source, "synthetic")
        self.assertIn("INTAKE_ID_COLLISION", " ".join(self.check()))

    def test_t4_two_canonical_records_same_ref_without_or_with_intake(self):
        self.bank["questions"][1]["extensions"][self.custody]["intake_ref"] = "q1"
        self.assertIn("ALIAS_COLLISION", " ".join(self.check(source=False)))
        with_intake = " ".join(self.check())
        self.assertIn("ALIAS_COLLISION", with_intake)
        self.assertIn("INTAKE_REF_REUSED", with_intake)
        self.assertIn("intake question q2", with_intake)

    def test_t5_missing_blank_malformed_and_non_object_intake_ids(self):
        for bad, marker in ((None, "INTAKE_ID_MISSING"), ("", "INTAKE_ID_MISSING"),
                            ("q 1", "INTAKE_ID_INVALID"), (23, "INTAKE_ID_MISSING"),
                            ("{bad}", "INTAKE_ID_INVALID")):
            with self.subTest(bad=bad):
                self.source["inputs"]["questions"][0]["id"] = bad
                with self.assertRaisesRegex(ValueError, marker):
                    owner_bank.new(self.source, "synthetic")
                self.assertIn(marker, " ".join(self.check()))
        self.source["inputs"]["questions"][0] = None
        with self.assertRaisesRegex(ValueError, "INTAKE_ID_INVALID"):
            owner_bank.new(self.source, "synthetic")

    def test_t5_blank_invalid_bank_ref_fails_without_intake(self):
        for bad, marker in (("", "intake_ref is required"), ("bad ref", "INTAKE_REF_INVALID"),
                            (None, "intake_ref is required")):
            with self.subTest(bad=bad):
                self.bank["questions"][0]["extensions"][self.custody]["intake_ref"] = bad
                self.assertIn(marker, " ".join(self.check(source=False)))

    def test_t7_foreign_ref_and_orphan(self):
        self.bank["questions"][0]["extensions"][self.custody]["intake_ref"] = "foreign"
        problems = " ".join(self.check())
        self.assertIn("not a question id in the intake", problems)
        self.assertIn("intake question q1", problems)

    def test_t7_dropped_occurrence_and_cardinality(self):
        self.bank["questions"].pop()
        problems = " ".join(self.check())
        self.assertIn("CARDINALITY_MISMATCH", problems)
        self.assertIn("intake question q2", problems)

    def test_t7_mutated_stem_and_digest(self):
        self.bank["questions"][0]["stem"] = "Entirely different invented sentence."
        self.assertIn("digest differs", " ".join(self.check(source=False)))
        self.bank["questions"][0]["extensions"][self.custody]["text_sha256"] = owner_bank.text_digest(
            self.bank["questions"][0]["stem"])
        self.assertIn("not the intake's text for q1", " ".join(self.check()))

    def test_t8_canonical_id_official_fields_and_direct_hints_still_rejected(self):
        self.bank["questions"][1]["id"] = self.bank["questions"][0]["id"]
        self.bank["questions"][0]["extensions"][self.custody]["exam"] = "SYNTHETIC EXAM"
        self.bank["questions"][0]["hints"] = ["Invented direct hint"]
        problems = " ".join(self.check())
        self.assertIn("duplicate id", problems)
        self.assertIn("official-exam fields", problems)
        self.assertIn("an owner question has no source", problems)

    def test_t9_missing_source_stem_sentinel_never_printed(self):
        sentinel = "NEVER_LEAK_SYNTHETIC_STEM_731942"
        self.source["inputs"]["questions"][1]["text"] = sentinel
        self.bank["questions"].pop()
        self.assertNotIn(sentinel, " ".join(self.check()))
        self.source["errors"] = [sentinel]
        with self.assertRaises(ValueError) as caught:
            owner_bank.new(self.source, "synthetic")
        self.assertNotIn(sentinel, str(caught.exception))

    def test_t10_blueprint_registry_and_no_intake_renderer_contract(self):
        registry = blueprints.load_registry()
        self.assertTrue(blueprints.blueprint_for_role(registry, "CORE2"))
        self.assertFalse(identity_errors(self.check(source=False)))
        self.bank["questions"][1]["extensions"][self.custody]["intake_ref"] = "q1"
        self.assertIn("ALIAS_COLLISION", " ".join(self.check(source=False)))

    def test_no_intake_does_not_guess_external_membership(self):
        self.bank["questions"][0]["extensions"][self.custody]["intake_ref"] = "unverifiable-but-valid"
        self.assertFalse(identity_errors(self.check(source=False)))
        self.assertIn("not a question id in the intake", " ".join(self.check(source=True)))

    def test_t11_cli_new_invalid_and_check_collision_nonzero_sanitized(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(owner_bank, "REPO", Path(temp)):
            root = Path(temp)
            input_file = root / "intake.json"
            output_file = root / "TEST/question-bank/synthetic.json"
            self.source["inputs"]["questions"][1]["id"] = "q1"
            input_file.write_text(json.dumps(self.source), encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                status = owner_bank.main(["new", "--intake", str(input_file), "--bank-id", "synthetic",
                                          "--out", str(output_file)])
            self.assertEqual(status, 1)
            self.assertIn("INTAKE_ID_COLLISION", stderr.getvalue())
            self.assertFalse(output_file.exists())
            bank_file = root / "identity.bank.json"
            self.bank["questions"][1]["extensions"][self.custody]["intake_ref"] = "q1"
            bank_file.write_text(json.dumps(self.bank), encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                status = owner_bank.main(["check", str(bank_file)])
            self.assertEqual(status, 1)
            self.assertIn("ALIAS_COLLISION", stdout.getvalue())


    def _malformed_check(self, bank, category, intake_value, complete):
        sentinel = "SYNTHETIC_SENTINEL_NO_ECHO_88431"
        outcomes = []
        for source in (None, intake_value):
            with self.subTest(category=category, with_intake=source is not None, complete=complete):
                problems = owner_bank.check(bank, intake=source, complete=complete)
                rendered = "\n".join(problems)
                self.assertIn(category, rendered)
                self.assertIn("questions[0]", rendered)
                self.assertNotIn(sentinel, rendered)
                outcomes.append(problems)
        return outcomes

    def test_t12_unhashable_canonical_id_list_is_fail_closed(self):
        bank = copy.deepcopy(self.bank)
        bank["questions"][0]["id"] = ["SYNTHETIC_SENTINEL_NO_ECHO_88431"]
        for complete in (False, True):
            self._malformed_check(bank, "CANONICAL_ID_INVALID", self.source, complete)
        # Combined mutant: a malformed canonical id must not mask invalid custody.
        bank["questions"][0]["extensions"][self.custody] = ["SYNTHETIC_SENTINEL_NO_ECHO_88431"]
        for complete in (False, True):
            rendered = "\n".join(owner_bank.check(bank, intake=self.source, complete=complete))
            self.assertIn("CANONICAL_ID_INVALID", rendered)
            self.assertIn("CUSTODY_MAPPING_INVALID", rendered)
            self.assertNotIn("SYNTHETIC_SENTINEL_NO_ECHO_88431", rendered)

    def test_t13_nonempty_list_extensions_is_fail_closed(self):
        bank = copy.deepcopy(self.bank)
        bank["questions"][0]["extensions"] = ["SYNTHETIC_SENTINEL_NO_ECHO_88431"]
        for complete in (False, True):
            self._malformed_check(bank, "EXTENSIONS_INVALID", self.source, complete)

    def test_t14_nonempty_list_custody_is_fail_closed_and_cli_nonzero(self):
        bank = copy.deepcopy(self.bank)
        bank["questions"][0]["extensions"][self.custody] = ["SYNTHETIC_SENTINEL_NO_ECHO_88431"]
        for complete in (False, True):
            self._malformed_check(bank, "CUSTODY_MAPPING_INVALID", self.source, complete)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.bank.json"
            path.write_text(json.dumps(bank), encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                result = owner_bank.main(["check", str(path)])
            self.assertEqual(result, 1)
            self.assertIn("CUSTODY_MAPPING_INVALID", stdout.getvalue())
            self.assertNotIn("SYNTHETIC_SENTINEL_NO_ECHO_88431", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
