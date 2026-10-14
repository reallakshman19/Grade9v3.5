#!/usr/bin/env python3
"""#182 R9: fast, read-only risk ledger preflight; never an academic verdict.

Only compares the integration ledger and witness bank against each other and
against the explicit R8 HOLD snapshot. This does NOT fetch author source blobs,
verify rendered HTML, decide academic demand, or authorize release.
"""
from __future__ import annotations

import copy
import json
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEMANDS = ("RETRIEVE", "EXPLAIN", "APPLY", "MODEL", "REPRESENT", "SYNTHESIZE", "JUSTIFY")
BANDS = ("D1", "D2", "D3", "D4")
ELEVATED = frozenset({
    "QRT-MODEL-D1", "QRT-SYNTHESIZE-D1", "QRT-JUSTIFY-D1",
    "QRT-RETRIEVE-D2", "QRT-MODEL-D2",
    "QRT-RETRIEVE-D3", "QRT-MODEL-D3", "QRT-RETRIEVE-D4",
})
RIVAL_BLOCKED = frozenset({
    "QRT-RETRIEVE-D1", "QRT-EXPLAIN-D1", "QRT-APPLY-D1",
    "QRT-MODEL-D1", "QRT-REPRESENT-D1", "QRT-SYNTHESIZE-D1",
    "QRT-REPRESENT-D2",
})
BLOCK_CODES = {"RIVAL_NOT_GROUNDED_IN_SOURCE", "SOURCE_RIVAL_VOCAB_INVALID"}
# R8 compiler holds seven source contracts; two D1 failures are implicit
# in author metadata, not declared via expected_source_hold_code.
COMPILER_ONLY_HOLDS = frozenset({"QRT-MODEL-D1", "QRT-SYNTHESIZE-D1"})
EXPLICIT_HOLD_MARKERS = RIVAL_BLOCKED - COMPILER_ONLY_HOLDS
OWNER_GOLDEN = "G-IMO-G9-FIVE-CORE-20261012"
GOLDEN_COMMIT = "6307e5dd97f9ae72a052fc7f3e88c368a4cc5434"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")


class DriftError(ValueError):
    """The pinned integration evidence is internally inconsistent or promoted."""


def require(ok: bool, code: str, cell: str = "") -> None:
    if not ok:
        raise DriftError(f"{code}: {cell}")


def index_rows(rows: list[dict], code: str) -> dict[str, dict]:
    entries: dict[str, dict] = {}
    for item in rows:
        cell = item.get("cell_id")
        require(isinstance(cell, str) and cell not in entries, code, str(cell))
        entries[cell] = item
    return entries


def verify(ledger: dict, witness_bank: dict) -> dict:
    """Fail closed on drift; never elevate source hypotheses to approval."""
    rows = index_rows(ledger["rows"], "R9_DUPLICATE_LEDGER_CELL")
    witnesses = index_rows(witness_bank["witnesses"], "R9_DUPLICATE_WITNESS_CELL")
    expected = {f"QRT-{d}-{b}" for d in DEMANDS for b in BANDS}
    require(set(rows) == expected and set(witnesses) == expected,
            "R9_28_CELL_DENOMINATOR_DRIFT")
    risk = {k for k, row in rows.items() if row.get("critical_educational_review_hold") is True}
    require(risk == ELEVATED, "R9_EIGHT_ELEVATED_HOLD_DRIFT", repr(sorted(risk ^ ELEVATED)))
    blocked = {k for k, w in witnesses.items() if w.get("expected_source_hold_code")}
    require(blocked == EXPLICIT_HOLD_MARKERS,
            "R9_FIVE_EXPLICIT_SOURCE_BLOCK_MARKERS_DRIFT",
            repr(sorted(blocked ^ EXPLICIT_HOLD_MARKERS)))
    require(ledger.get("authority") == "v3.1.0 / label_sha 2ff9246" and
            witness_bank.get("authority") == "TEST_PROPOSED_UNREVIEWED",
            "R9_AIM_OR_WITNESS_AUTHORITY_CHANGED")
    for cid in sorted(expected):
        row, w = rows[cid], witnesses[cid]
        source, manifest, pin = row["source"], row["manifest"], w["source_pin"]
        require(source.get("classification") == "AUTHORED_TEST_ONLY" and
                source.get("path") == pin.get("source_path") and
                source.get("git_blob_sha") == pin.get("source_blob") and
                manifest.get("path") == pin.get("manifest_path") and
                manifest.get("git_blob_sha") == pin.get("manifest_blob") and
                source.get("commit") in (pin.get("commit"), w.get("source_alternate_commit")),
                "R9_SOURCE_MANIFEST_WITNESS_PIN_DRIFT", cid)
        require(all(SHA40.fullmatch(s) for s in
                    (source["commit"], source["git_blob_sha"], manifest["git_blob_sha"])),
                "R9_MALFORMED_SOURCE_SHA", cid)
        require(source["path"].startswith("TEST/") and
                manifest["path"].startswith("TEST/products/"),
                "R9_UNAUTHORISED_SOURCE_SCOPE", cid)
        require(w.get("strongest_rival") in DEMANDS and
                w["strongest_rival"] != cid.split("-")[1] and
                w.get("primary_crux_move_ref") and w.get("transfer_crux_move_ref") and
                w["primary_crux_move_ref"] != w["transfer_crux_move_ref"] and
                len(w.get("question_specific_W", "")) >= 35,
                "R9_QUESTION_RIVAL_OR_W_MISSING", cid)
        if cid in blocked:
            require(w.get("expected_source_hold_code") in BLOCK_CODES,
                    "R9_UNRECOGNISED_SOURCE_BLOCK", cid)
        else:
            require(not w.get("expected_source_hold_code"),
                    "R9_UNEXPECTED_SOURCE_BLOCK", cid)
        issue = 211 if cid in {"QRT-MODEL-D2", "QRT-RETRIEVE-D2"} else (
            214 if cid.endswith("-D2") else 234)
        require(row.get("independent_reviewer_nomination_issue") == issue,
                "R9_INCORRECT_REVIEWER_ROUTE", cid)
        require(row.get("academic_review") == "QUALIFIED_INDEPENDENT_REVIEW_PENDING" and
                row.get("owner_qrta_accepted") is False and
                row.get("release_authorized") is False and
                row.get("owner_golden_designated") is False and
                row.get("qualified_independent_signed_verdict_id") is None and
                row.get("nominated_independent_reviewer") is None,
                "R9_FALSE_ACADEMIC_OR_OWNER_PROMOTION", cid)
        golden = row.get("frozen_golden", {})
        require(golden.get("id") == OWNER_GOLDEN and
                golden.get("commit") == GOLDEN_COMMIT and
                golden.get("semantic_technique_verdict") == "UNREVIEWED",
                "R9_GOLDEN_SCOPE_OR_STATUS_DRIFT", cid)
    return {"checked": 28, "elevated": 8, "source_blocked": 7,
            "explicit_hold_markers": 5, "compiler_only_holds": 2,
            "contract_proposals": 21, "independent_approvals": 0,
            "owner_acceptances": 0, "release": "HOLD",
            "source_bytes_verified": False, "native_html_verified": False}


class R9RiskPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads((HERE / "r5-01-28-artifact-adoption.v1.json").read_text())
        cls.bank = json.loads((HERE / "qrt-intent-witnesses-pilot.v1.json").read_text())

    def test_real_r8_snapshot_passes_without_approving_anyone(self):
        self.assertEqual(verify(self.ledger, self.bank), {
            "checked": 28, "elevated": 8, "source_blocked": 7,
            "explicit_hold_markers": 5, "compiler_only_holds": 2,
            "contract_proposals": 21, "independent_approvals": 0,
            "owner_acceptances": 0, "release": "HOLD",
            "source_bytes_verified": False, "native_html_verified": False})

    def reject(self, code, change):
        ledger, bank = copy.deepcopy(self.ledger), copy.deepcopy(self.bank)
        change(ledger, bank)
        with self.assertRaisesRegex(DriftError, "^" + code + ":"):
            verify(ledger, bank)

    def test_negative_drop_one_of_28(self):
        self.reject("R9_28_CELL_DENOMINATOR_DRIFT", lambda a, b: a["rows"].pop())

    def test_negative_duplicate_witness(self):
        self.reject("R9_DUPLICATE_WITNESS_CELL", lambda a, b: b["witnesses"].append(copy.deepcopy(b["witnesses"][0])))

    def test_negative_discard_elevated_hold(self):
        self.reject("R9_EIGHT_ELEVATED_HOLD_DRIFT", lambda a, b: next(x for x in a["rows"] if x["cell_id"] == "QRT-MODEL-D2").update(critical_educational_review_hold=False))

    def test_negative_remove_rival_hold(self):
        self.reject("R9_FIVE_EXPLICIT_SOURCE_BLOCK_MARKERS_DRIFT", lambda a, b: next(x for x in b["witnesses"] if x["cell_id"] == "QRT-REPRESENT-D2").pop("expected_source_hold_code"))

    def test_negative_forge_source_blob(self):
        self.reject("R9_SOURCE_MANIFEST_WITNESS_PIN_DRIFT", lambda a, b: a["rows"][0]["source"].update(git_blob_sha="0"*40))

    def test_negative_forge_manifest_blob(self):
        self.reject("R9_SOURCE_MANIFEST_WITNESS_PIN_DRIFT", lambda a, b: a["rows"][0]["manifest"].update(git_blob_sha="0"*40))

    def test_negative_fake_academic_signature(self):
        self.reject("R9_FALSE_ACADEMIC_OR_OWNER_PROMOTION", lambda a, b: a["rows"][0].update(qualified_independent_signed_verdict_id="fake-accepted"))

    def test_negative_fake_owner_acceptance(self):
        self.reject("R9_FALSE_ACADEMIC_OR_OWNER_PROMOTION", lambda a, b: a["rows"][0].update(owner_qrta_accepted=True))

    def test_negative_replace_frozen_golden(self):
        self.reject("R9_GOLDEN_SCOPE_OR_STATUS_DRIFT", lambda a, b: a["rows"][0]["frozen_golden"].update(commit="0"*40))

    def test_negative_misroute_reviewer(self):
        self.reject("R9_INCORRECT_REVIEWER_ROUTE", lambda a, b: next(x for x in a["rows"] if x["cell_id"] == "QRT-MODEL-D2").update(independent_reviewer_nomination_issue=214))


if __name__ == "__main__":
    unittest.main()
