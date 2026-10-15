#!/usr/bin/env python3
"""PR-head renderer candidate over the 21 independently SHA-pinned R8 TEST sources.

THIS IS A REVIEW-GATED HARNESS, NOT A GOLDEN UPDATE, OWNER ACCEPTANCE, OR RELEASE.
The old R8 21-cell original-source renderer run remains untouched. This distinct
manual-only qualification runs each pinned source in an isolated temporary git
worktree and overlays ONLY the current PR-head Shared/tools/render_core.py.
A count has NO admissible standing until Agent B checks this exact harness SHA.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from html.parser import HTMLParser


# Identical root/cell assignments to the pre-existing R8 P2b shell step.
CASES = (
    ("source-explain-d3", "explain-d3"),
    ("source-model-d2", "model-d2"),
    ("source-retrieve-d2", "retrieve-d2"),
    ("source-retrieve-d4", "retrieve-d4"),
    ("source-justify-d1", "justify-d1"),
    ("source-explain-d3", "retrieve-d3"),
    ("source-explain-d3", "model-d3"),
    ("source-d2-common", "explain-d2"),
    ("source-d2-common", "apply-d2"),
    ("source-d2-common", "synthesize-d2"),
    ("source-d2-common", "justify-d2"),
    ("source-explain-d3", "apply-d3"),
    ("source-explain-d3", "represent-d3"),
    ("source-d3-synthesize", "synthesize-d3"),
    ("source-explain-d3", "justify-d3"),
    ("source-d4-explain", "explain-d4"),
    ("source-d4-apply", "apply-d4"),
    ("source-d4-model", "model-d4"),
    ("source-d4-represent", "represent-d4"),
    ("source-d4-synthesize", "synthesize-d4"),
    ("source-d4-justify", "justify-d4"),
)
RECONCILIATION = Path("TEST/imo-research/qrt-tiles/reconciliation")
RENDERER = Path("Shared/tools/render_core.py")
WORKFLOW = Path(".github/workflows/imo182-r8-qrt-intent-contract.yml")

# Owner AB-R14-SRCPIN: preserve draft #191 original input provenance only
# for R14. The existing #201 R8 checkout remains on its later evidence SHA.
R14_RETRIEVE_D2_ROOT = "source-retrieve-d2-r14-original"
R14_RETRIEVE_D2_SOURCE_COMMIT = "eb3cf06646f00bf208084e794b41b4d8d83135b6"
R8_RETRIEVE_D2_SOURCE_COMMIT = "5b382356e792ae50884241fb047c328e304d011d"


def r14_source_root(root: str, slug: str) -> str:
    """Return the distinct ORIGINAL checkout for R14 RETRIEVE-D2 only."""
    if (root, slug) == ("source-retrieve-d2", "retrieve-d2"):
        return R14_RETRIEVE_D2_ROOT
    return root


def verify_r14_source_isolation() -> None:
    """Reject authority drift in both frozen source commits and checkout scopes."""
    workflow = WORKFLOW.read_text(encoding="utf-8")
    r8_checkout = "- name: Exact RETRIEVE-D2 authored TEST source from established method-cue benchmark\n        uses: actions/checkout@v4\n        with:\n          ref: 5b382356e792ae50884241fb047c328e304d011d\n          path: source-retrieve-d2\n          persist-credentials: false"
    r14_checkout = "- name: R14-only RETRIEVE-D2 original authored TEST source (AB-R14-SRCPIN)\n        if: github.event_name == 'workflow_dispatch'\n        uses: actions/checkout@v4\n        with:\n          ref: eb3cf06646f00bf208084e794b41b4d8d83135b6\n          path: source-retrieve-d2-r14-original\n          persist-credentials: false"
    if (workflow.count(r8_checkout) != 1 or workflow.count(r14_checkout) != 1
            or R14_RETRIEVE_D2_ROOT in {root for root, _ in CASES}
            or [(root, slug) for root, slug in CASES
                if r14_source_root(root, slug) != root] != [
                    ("source-retrieve-d2", "retrieve-d2")]):
        raise AssertionError("R14_ORIGINAL_SOURCE_CHECKOUT_PIN_DRIFT")
    bank = json.loads((RECONCILIATION / "qrt-intent-witnesses-pilot.v1.json")
                      .read_text(encoding="utf-8"))
    witness = [entry for entry in bank["witnesses"]
               if entry["cell_id"] == "QRT-RETRIEVE-D2"]
    if (len(witness) != 1
            or witness[0]["source_pin"]["commit"] != R14_RETRIEVE_D2_SOURCE_COMMIT
            or witness[0]["source_alternate_commit"] != R8_RETRIEVE_D2_SOURCE_COMMIT):
        raise AssertionError("R14_ORIGINAL_WITNESS_SOURCE_PIN_DRIFT")




# Only structural rejection codes already defined by qrt_intent_native_evidence.py.
# Neither arbitrary child output nor original question text is logged or uploaded.
SAFE_NATIVE_FAILURE_CODES = frozenset((
    "UNVALIDATED_QRT_CONTRACT",
    "PATH_ESCAPE",  # Audited qrt_intent_contract.ensure() identifiers
    "SOURCE_MISSING",
    "SOURCE_CHANGED_SINCE_CONTRACT",
    "MANIFEST_CHANGED_SINCE_CONTRACT",
    "REGISTRY_CHANGED_SINCE_CONTRACT",
    "IMMUTABLE_GOLDEN_LOCK_DRIFT",
    "WRONG_FROZEN_GOLDEN",
    "RENDER_RECEIPT_MISSING",
    "RENDERER_AUTHORITY_OR_GAPS",
    "RENDER_RECEIPT_ROLES_OR_PAGES",
    "RENDER_RECEIPT_SHA_SET_DRIFT",
    "MALFORMED_RENDER_RECEIPT_SHAS",
    "LEGACY_RECEIPT_REQUIRES_INDEPENDENT_RERENDER",
    "INDEPENDENT_RECEIPT_CHANGED",
    "INDEX_MISSING",
    "INDEX_SHA_NOT_RECEIPT",
    "LEGACY_INDEX_NONDETERMINISTIC",
    "MISSING_NATIVE_ROLE",
    "NATIVE_PAGE_SHA_NOT_RECEIPT",
    "LEGACY_CORE_NONDETERMINISTIC",
    "GOLDEN_ROLE_NOT_UNIQUE",
    "GOLDEN_SNAPSHOT_BYTES_DRIFT",
    "ROLE_BLUEPRINT_MISMATCH",
    "GOLDEN_SLOT_MISMATCH",
    "GOLDEN_COMPONENT_MISMATCH",
    "CORE1B_GOLDEN_RECONSTRUCTION_DRIFT",
))
SAFE_FAILURE_FALLBACKS = (
    ("ModuleNotFoundError:", "CHILD_MODULE_NOT_FOUND"),
    ("ContractError:", "CHILD_CONTRACT_ERROR_UNCLASSIFIED"),
    ("AssertionError:", "CHILD_ASSERTION_UNCLASSIFIED"),
    ("FileNotFoundError:", "CHILD_FILE_NOT_FOUND"),
    ("KeyError:", "CHILD_KEY_NOT_FOUND"),
    ("JSONDecodeError:", "CHILD_JSON_DECODE_FAILURE"),
)


# A failure in a specific rendered role is diagnostic, not a source-pin override.
# Provenance, receipt-integrity, unclassified errors and infrastructure errors
# MUST abort the remaining executions; they can never be treated as case-local.
CASE_LOCAL_FAILURE_CODES = frozenset((
    "GOLDEN_COMPONENT_MISMATCH",
    "GOLDEN_SLOT_MISMATCH",
    "ROLE_BLUEPRINT_MISMATCH",
    "CORE1B_GOLDEN_RECONSTRUCTION_DRIFT",
))
CASE_STATUSES = frozenset(("PASS", "FAIL", "NOT_REACHED"))

# Every persisted systemic type/code is drawn from this fixed audited vocabulary.
# Never serialize arbitrary exception names, args, paths, child output, or traceback.
SAFE_CHILD_ASSERTION_TYPES = frozenset((
    "ContractError", "AssertionError", "RuntimeError",
    "ModuleNotFoundError", "FileNotFoundError", "KeyError",
    "JSONDecodeError", "UNCLASSIFIED",
))
SAFE_CHILD_FAILURE_CODES = (
    SAFE_NATIVE_FAILURE_CODES
    | frozenset(code for _marker, code in SAFE_FAILURE_FALLBACKS)
    | {"UNCLASSIFIED_SUBPROCESS_FAILURE"}
)
SAFE_HARNESS_ASSERTION_CODES = frozenset((
    "R14_WRONG_CASE_EXCEPTION",
    "R14_FANOUT_RECORD_INTEGRITY",
    "R14_DIAGNOSTIC_PHASE_OR_CELL_NOT_PINNED",
    "PR_HEAD_CASE_MAP_DRIFT_FROM_FROZEN_R8",
    "SOURCE_COMMIT_CHANGED",
    "SOURCE_MANIFEST_OR_PACKAGE_BLOB_CHANGED",
    "ORIGINAL_QRT_28_WITNESSES_DRIFT",
    "SOURCE_HELD_SEVEN_MUST_REMAIN_HELD",
    "ORIGINAL_QRT_28_WITNESS_DUPLICATION",
    "OVERLAY_MANIFEST_BLOB_CHANGED",
    "OVERLAY_QUESTION_SOURCE_BLOB_CHANGED",
    "SELECTED_ORIGINAL_QUESTION_DRIFT",
    "PR_HEAD_SOURCE_QID_NOT_PINNED",
    "ASSISTED_RETURN_FALSE_INDEPENDENT_CREDIT",
))
SYSTEMIC_BUILTIN_CODES = {
    "AssertionError": "SYSTEMIC_ASSERTION_UNCLASSIFIED",
    "RuntimeError": "SYSTEMIC_RUNTIME_ERROR_UNCLASSIFIED",
    "FileNotFoundError": "SYSTEMIC_FILE_NOT_FOUND",
    "PermissionError": "SYSTEMIC_PERMISSION_ERROR",
    "KeyError": "SYSTEMIC_KEY_NOT_FOUND",
    "JSONDecodeError": "SYSTEMIC_JSON_DECODE_FAILURE",
    "ModuleNotFoundError": "SYSTEMIC_MODULE_NOT_FOUND",
    "OSError": "SYSTEMIC_OS_ERROR",
    "ValueError": "SYSTEMIC_VALUE_ERROR",
    "TypeError": "SYSTEMIC_TYPE_ERROR",
}
SAFE_SYSTEMIC_FAILURE_CODES = (
    SAFE_CHILD_FAILURE_CODES | SAFE_HARNESS_ASSERTION_CODES
    | frozenset(SYSTEMIC_BUILTIN_CODES.values())
    | {"SYSTEMIC_ABORT_UNCLASSIFIED"}
)
SAFE_SYSTEMIC_TYPES = SAFE_CHILD_ASSERTION_TYPES | frozenset(
    SYSTEMIC_BUILTIN_CODES
)



class CaseLocalFailure(RuntimeError):
    """Explicit audited technical failure for one pinned case only."""

    def __init__(self, phase: str, cell_id: str, kind: str, code: str):
        assert code in CASE_LOCAL_FAILURE_CODES
        self.phase, self.cell_id, self.kind, self.code = (
            phase, cell_id, kind, code)
        super().__init__(f"R14_CASE_LOCAL {phase} {cell_id} {kind}: {code}")


class ChildProcessFailure(RuntimeError):
    """A nonlocal child rejection with independently sanitized type/code only."""

    def __init__(self, phase: str | None, kind: str, code: str):
        if kind not in SAFE_CHILD_ASSERTION_TYPES or code not in SAFE_CHILD_FAILURE_CODES:
            raise AssertionError("R14_CHILD_FAILURE_CLASSIFIER_NOT_ALLOWLISTED")
        self.kind, self.code = kind, code
        super().__init__(
            f"R14 child rejected ({phase or 'unknown-phase'}): "
            f"{kind}: {code} [untrusted detail redacted]"
        )


def source_safe_systemic_exception(exc: Exception) -> tuple[str, str]:
    """Preserve REAL audited type/code, but neither detail nor guessed code.

    A wrapped child already has a sanitized terminator classification.
    A local AssertionError is admissible only when its entire message equals
    an audited harness invariant. Any other exception gets a fixed safe code.
    """
    if isinstance(exc, ChildProcessFailure):
        return exc.kind, exc.code
    kind = type(exc).__name__
    if kind not in SYSTEMIC_BUILTIN_CODES:
        return "UNCLASSIFIED", "SYSTEMIC_ABORT_UNCLASSIFIED"
    if kind == "AssertionError" and str(exc) in SAFE_HARNESS_ASSERTION_CODES:
        return "AssertionError", str(exc)
    return kind, SYSTEMIC_BUILTIN_CODES[kind]



# R14 evidence-only marker observation: read rendered/snapshot HTML privately,
# emit only counts, stable digests of marker identifiers and mismatch positions.
# Never serialize HTML, question content, free-form attribute values or paths.
ROLES_FOR_COMPONENT_DIFF = ("CORE1", "CORE1A", "CORE1B", "CORE2A", "CORE2B")
GOLDEN_COMPONENT_ROOT = Path("golden/units/G-IMO-G9-FIVE-CORE-20261012")


class _ComponentOnlyParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.components: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        value = dict(attrs).get("data-g9-component")
        if value:
            # It is used internally only for equality and a SHA digest;
            # contents are never printed or written to JSON.
            self.components.append(value)


def _component_tokens(path: Path) -> list[str]:
    parser = _ComponentOnlyParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.components


def source_safe_component_delta(source_root: Path, target: Path) -> dict:
    """Observations, not a golden verdict; no user question or raw HTML."""
    lock_dir = source_root / GOLDEN_COMPONENT_ROOT
    lock = json.loads((lock_dir / "snapshot-lock.json").read_text(encoding="utf-8"))
    records = lock["snapshots"]
    if (len(records) != 5
            or {row["role"] for row in records} != set(ROLES_FOR_COMPONENT_DIFF)):
        raise AssertionError("R14_COMPONENT_DIFF_LOCK_UNRECOGNIZED")
    evidence = []
    for role in ROLES_FOR_COMPONENT_DIFF:
        rec = next(item for item in records if item["role"] == role)
        # All snapshot filenames are constrained by the locked role identity.
        expected_snapshot = "snapshots/" + role.lower() + ".html"
        if rec["path"] != expected_snapshot:
            raise AssertionError("R14_COMPONENT_DIFF_SNAPSHOT_PATH_DRIFT")
        golden = _component_tokens(lock_dir / expected_snapshot)
        actual = _component_tokens(target / (role.lower() + ".html"))
        bound = min(len(golden), len(actual))
        first = next((i for i in range(bound) if golden[i] != actual[i]), None)
        if first is None and len(golden) != len(actual):
            first = bound
        def digest(ids: list[str]) -> str:
            return hashlib.sha256(bytes([0]).join(value.encode("utf-8") for value in ids)).hexdigest()
        evidence.append({
            "role": role,
            "golden_component_count": len(golden),
            "candidate_component_count": len(actual),
            "golden_component_id_sha256": digest(golden),
            "candidate_component_id_sha256": digest(actual),
            "first_difference_zero_based": first,
            "component_ids_match": golden == actual,
        })
    return {
        "schema": "imo182-r14-component-marker-diagnostic/v1",
        "source_safe": True,
        "scope": "MARKER_IDS_ONLY_NOT_HTML_OR_ACADEMIC",
        "golden_modified": False,
        "renderer_modified": False,
        "roles": evidence,
        "all_roles_match": all(row["component_ids_match"] for row in evidence),
        "academic_accepted": 0,
        "release": "HOLD",
    }


def cleanup_shadow_worktrees(
    overlays: dict[str, tuple[Path, Path]], remover
) -> list[dict]:
    """Use each shadow's owning git repository; never mask aggregate evidence.

    A failing git remove yields a sanitized FAIL record, and cleanup continues.
    Root identifiers are allowlisted literals from the pinned CASES mapping.
    """
    allowed = {root for root, _slug in CASES}
    failures: list[dict] = []
    for root, (owner, shadow) in overlays.items():
        try:
            if root not in allowed or not isinstance(owner, Path) or not isinstance(shadow, Path):
                raise AssertionError("R14_CLEANUP_OWNER_MAP_DRIFT")
            remover(["git", "-C", str(owner), "worktree", "remove",
                     "--force", str(shadow)])
        except Exception as exc:
            kind, code = source_safe_systemic_exception(exc)
            failures.append({
                "case_source_root": root if root in allowed else "UNCLASSIFIED",
                "assertion_type": kind,
                "failure_code": code,
                "raw_git_stderr_recorded": False,
            })
    return failures


def write_fanout_aggregate(
    out: Path, reports: list[dict], systemic_abort: bool, cleanup_failures: list[dict],
    held: set[str], head: str, renderer_digest: str,
) -> bool:
    """Write the aggregate atomically EVEN if some git worktree removes fail."""
    summary = {status: sum(r["status"] == status for r in reports)
               for status in ("PASS", "FAIL", "NOT_REACHED")}
    assert len(reports) == 21 and sum(summary.values()) == 21
    assert len({r["cell_id"] for r in reports}) == 21
    assert len(held) == 7
    assert {r["cell_id"] for r in reports}.isdisjoint(held)
    failed = (systemic_abort or summary["FAIL"] > 0
              or summary["NOT_REACHED"] > 0 or bool(cleanup_failures))
    result = {
        "schema": "imo182-prhead-overlay-fanout-diagnostic/v1",
        "disposition": ("FAIL_RUN_HOLD_ALL_21_NO_RENDERER_VERDICT" if failed
                        else "PROVISIONAL_AGENT_B_AND_OWNER_GATES_REQUIRED"),
        "renderer_head_sha": head,
        "renderer_sha256": renderer_digest,
        "historical_r8_and_frozen_golden_unchanged": True,
        "source_pinned_original_cells": 21,
        "source_held_no_candidate_render": sorted(held),
        "observed_diagnostic_counts": summary,
        "native_returns_observed_not_accepted": sum(
            bool(r["candidate_round_trip"]) for r in reports),
        "candidate_counts_admissible_before_agent_b": False,
        "systemic_abort": systemic_abort,
        "cleanup_disposition": "FAIL" if cleanup_failures else "PASS",
        "cleanup_failure_count": len(cleanup_failures),
        "cleanup_failures": cleanup_failures,
        "academic_accepted": 0,
        "owner_qrt_accepted": 0,
        "release": "HOLD",
        "cells": reports,
    }
    stage = out.with_name(out.name + ".tmp")
    stage.write_text(json.dumps(result, indent=2, ensure_ascii=False) + chr(10),
                     encoding="utf-8")
    stage.replace(out)
    return failed


def cleanup_and_component_self_test() -> None:
    """Synthetic owner-map/failing-remove/aggregate and marker redaction tests."""
    with tempfile.TemporaryDirectory(prefix="r14-cleanup-component-synthetic-") as td:
        root = Path(td)
        owner = root / R14_RETRIEVE_D2_ROOT
        old_r8 = root / "source-retrieve-d2"
        shadow = root / "overlay-for-retrieve-d2"
        other_owner = root / "source-explain-d3"
        other_shadow = root / "overlay-for-explain-d3"
        visited = []
        secret = "ORIGINAL_QUESTION_CONTENT_MUST_NOT_ESCAPE"

        def failing_remove(cmd):
            visited.append(cmd)
            if cmd[2] == str(owner):
                raise ChildProcessFailure(None, "UNCLASSIFIED",
                                          "UNCLASSIFIED_SUBPROCESS_FAILURE")
            if cmd[2] == str(other_owner):
                return ""
            raise AssertionError("R14_CLEANUP_WRONG_REPOSITORY")

        failures = cleanup_shadow_worktrees({
            "source-retrieve-d2": (owner, shadow),
            "source-explain-d3": (other_owner, other_shadow)
        }, failing_remove)
        assert len(visited) == 2
        assert visited[0] == ["git", "-C", str(owner), "worktree", "remove",
                              "--force", str(shadow)]
        assert visited[0][2] != str(old_r8)
        assert visited[1][2] == str(other_owner)
        assert failures == [{
            "case_source_root": "source-retrieve-d2",
            "assertion_type": "UNCLASSIFIED",
            "failure_code": "UNCLASSIFIED_SUBPROCESS_FAILURE",
            "raw_git_stderr_recorded": False,
        }]
        observed = [{"cell_id": "QRT-" + slug.upper(),
                     "status": "PASS", "candidate_round_trip": True}
                    for _, slug in CASES]
        held = {"QRT-" + slug for slug in ("APPLY-D1", "EXPLAIN-D1",
                "MODEL-D1", "REPRESENT-D1", "REPRESENT-D2",
                "RETRIEVE-D1", "SYNTHESIZE-D1")}
        aggregate = root / "aggregate.json"
        assert write_fanout_aggregate(aggregate, observed, False, failures,
                                     held, "synthetic", "synthetic") is True
        disk = json.loads(aggregate.read_text(encoding="utf-8"))
        assert disk["observed_diagnostic_counts"] == {
            "PASS": 21, "FAIL": 0, "NOT_REACHED": 0}
        assert disk["cleanup_disposition"] == "FAIL"
        assert disk["cleanup_failure_count"] == 1
        assert disk["candidate_counts_admissible_before_agent_b"] is False
        assert disk["release"] == "HOLD"
        assert secret not in json.dumps(disk)
        assert write_fanout_aggregate(aggregate, observed, False, [],
                                     held, "synthetic", "synthetic") is False
        assert json.loads(aggregate.read_text(encoding="utf-8"))["cleanup_disposition"] == "PASS"
        # Test component-marker parser with synthetic invented markers only,
        # never original source/golden HTML in this regression.
        golden = root / GOLDEN_COMPONENT_ROOT
        snapshots = golden / "snapshots"
        snapshots.mkdir(parents=True)
        pages = root / "synthetic-pages"
        pages.mkdir()
        entries = []
        for role in ROLES_FOR_COMPONENT_DIFF:
            page = role.lower() + ".html"
            entries.append({"role": role, "path": "snapshots/" + page})
            base = '<article data-g9-component="IDENTITY"></article>'
            (snapshots / page).write_text(base, encoding="utf-8")
            extra = ('<span data-g9-component="SECTION_ROUTE"></span>'
                     if role == "CORE1A" else "")
            (pages / page).write_text(base + extra + secret, encoding="utf-8")
        (golden / "snapshot-lock.json").write_text(
            json.dumps({"snapshots": entries}), encoding="utf-8")
        diff = source_safe_component_delta(root, pages)
        assert diff["all_roles_match"] is False
        assert len(diff["roles"]) == 5
        assert [r["role"] for r in diff["roles"] if not r["component_ids_match"]] == ["CORE1A"]
        assert next(r for r in diff["roles"] if r["role"] == "CORE1A")[
            "first_difference_zero_based"] == 1
        assert secret not in json.dumps(diff)
        assert "<article" not in json.dumps(diff)
    print("R14 owned-worktree cleanup, preserved aggregate and safe component delta: PASS")


def case_receipt(out: Path, slug: str, record: dict) -> None:
    """Atomically persist one audited per-case JSON receipt, never raw HTML."""
    assert slug in {entry[1] for entry in CASES}
    assert record["cell_id"] == "QRT-" + slug.upper()
    assert record["status"] in CASE_STATUSES
    if record["status"] == "FAIL":
        assert record["failure_code"] in (
            CASE_LOCAL_FAILURE_CODES | SAFE_SYSTEMIC_FAILURE_CODES
            | {"TECHNICAL_ROUND_TRIP_INCOMPLETE"})
        assert record.get("assertion_type", "UNCLASSIFIED") in SAFE_SYSTEMIC_TYPES
    target = out.with_name("prhead-overlay-" + slug + "-CASE.json")
    staging = target.with_name(target.name + ".tmp")
    staging.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    staging.replace(target)


def fanout_cases(execute, verify_pin, persist) -> tuple[list[dict], bool]:
    """Observe all 21 unless an actual systemic/custody failure stops work.

    All statuses are diagnostic only. An aborted run still emits 21 records,
    marking unattempted cells NOT_REACHED, without pretending they failed.
    """
    reports: list[dict] = []
    systemic_abort = False
    for root, slug in CASES:
        cell_id = "QRT-" + slug.upper()
        if systemic_abort:
            record = {"cell_id": cell_id, "status": "NOT_REACHED",
                      "phase": "systemic-abort", "failure_code": None,
                      "candidate_round_trip": False}
        else:
            try:
                try:
                    record = execute(root, slug)
                    verify_pin(root, slug)
                except CaseLocalFailure as failure:
                    # If the underlying source changed while processing, the
                    # apparent local mismatch is a systemic source-custody fault.
                    verify_pin(root, slug)
                    if failure.cell_id != cell_id:
                        raise AssertionError("R14_WRONG_CASE_EXCEPTION")
                    record = {"cell_id": cell_id, "status": "FAIL",
                              "phase": failure.phase,
                              "assertion_type": failure.kind,
                              "failure_code": failure.code,
                              "candidate_round_trip": False}
            except Exception as exc:
                # Keep the actual AUDITED class/code; never its raw message,
                # child output, file path, question, or traceback. No recovery
                # or further case execution after a systemic/custody failure.
                systemic_abort = True
                assertion_kind, code = source_safe_systemic_exception(exc)
                record = {"cell_id": cell_id, "status": "FAIL",
                          "phase": "systemic-abort",
                          "abort_kind": "SYSTEMIC_ABORT",
                          "assertion_type": assertion_kind,
                          "failure_code": code,
                          "candidate_round_trip": False}
        if record["cell_id"] != cell_id or record["status"] not in CASE_STATUSES:
            raise AssertionError("R14_FANOUT_RECORD_INTEGRITY")
        persist(slug, record)
        reports.append(record)
    assert len(reports) == 21
    assert len({r["cell_id"] for r in reports}) == 21
    return reports, systemic_abort


def fanout_self_test() -> None:
    """Case-specific early/middle/late failure and systemic-stop controls."""
    with tempfile.TemporaryDirectory(prefix="r14-21-fanout-synthetic-") as td:
        output = Path(td) / "AGGREGATE.json"
        secret = "ORIGINAL_QUESTION_CONTENT_MUST_NOT_ESCAPE"

        def execute_for(fails, systemic_at=None, systemic_error=None):
            visited = []

            def synthetic_execute(root, slug):
                visited.append(slug)
                if slug == systemic_at:
                    if systemic_error is not None:
                        raise systemic_error
                    raise RuntimeError(secret)
                if slug in fails:
                    raise CaseLocalFailure("native-evidence", "QRT-" + slug.upper(),
                                           "ContractError", "GOLDEN_COMPONENT_MISMATCH")
                return {"cell_id": "QRT-" + slug.upper(), "status": "PASS",
                        "phase": "browser-navigation", "failure_code": None,
                        "candidate_round_trip": True}

            def verify_pin(_root, _slug):
                return None

            seen, aborted = fanout_cases(
                synthetic_execute, verify_pin,
                lambda slug, record: case_receipt(output, slug, record))
            for root, slug in CASES:
                receipt = json.loads(output.with_name(
                    "prhead-overlay-" + slug + "-CASE.json").read_text(
                        encoding="utf-8"))
                assert receipt == next(x for x in seen
                                       if x["cell_id"] == "QRT-" + slug.upper())
                assert secret not in json.dumps(receipt)
            return seen, aborted, visited

        all_pass, stopped, visited = execute_for(set())
        assert len(visited) == 21 and not stopped
        assert sum(x["status"] == "PASS" for x in all_pass) == 21
        for position in (0, 10, 20):
            failing_slug = CASES[position][1]
            records, stopped, visited = execute_for({failing_slug})
            assert len(visited) == 21 and not stopped
            assert sum(x["status"] == "FAIL" for x in records) == 1
            assert records[position]["failure_code"] == "GOLDEN_COMPONENT_MISMATCH"
            assert sum(x["status"] == "PASS" for x in records) == 20
        middle = CASES[10][1]
        records, stopped, visited = execute_for(set(), systemic_at=middle)
        assert stopped and len(visited) == 11
        assert records[10]["abort_kind"] == "SYSTEMIC_ABORT"
        assert records[10]["assertion_type"] == "RuntimeError"
        assert records[10]["failure_code"] == "SYSTEMIC_RUNTIME_ERROR_UNCLASSIFIED"
        assert all(x["status"] == "NOT_REACHED" for x in records[11:])
        assert len(records) == 21
        assert all(not x["candidate_round_trip"] for x in records[10:])
        # Do not leak secret through an unknown exception type or its args.
        class UntrustedError(Exception):
            pass
        records, stopped, visited = execute_for(
            set(), systemic_at=middle, systemic_error=UntrustedError(secret))
        assert stopped and len(visited) == 11
        assert records[10]["assertion_type"] == "UNCLASSIFIED"
        assert records[10]["failure_code"] == "SYSTEMIC_ABORT_UNCLASSIFIED"
        # Preserve ONLY an audited, exact harness-assertion code.
        assert source_safe_systemic_exception(
            AssertionError("SOURCE_MANIFEST_OR_PACKAGE_BLOB_CHANGED")) == (
                "AssertionError", "SOURCE_MANIFEST_OR_PACKAGE_BLOB_CHANGED")
        assert source_safe_systemic_exception(
            AssertionError("SOURCE_COMMIT_CHANGED: " + secret)) == (
                "AssertionError", "SYSTEMIC_ASSERTION_UNCLASSIFIED")
        assert source_safe_systemic_exception(
            FileNotFoundError(secret)) == (
                "FileNotFoundError", "SYSTEMIC_FILE_NOT_FOUND")
        assert source_safe_systemic_exception(
            KeyError(secret)) == ("KeyError", "SYSTEMIC_KEY_NOT_FOUND")

        # A real imported ContractError child (not a mocked return value)
        # must preserve its allowlisted systemic code across the production
        # call(), the individual case receipt, and the on-disk child receipt.
        child = (
            "from qrt_intent_contract import ContractError\n"
            "raise ContractError('SOURCE_CHANGED_SINCE_CONTRACT: "
            + secret + "')\n"
        )
        source_dir = Path(__file__).resolve().parent
        native_diag = Path(td) / "real-systemic-child-FAILURE-CODE.json"
        def real_systemic_case(_root, slug):
            call([sys.executable, "-c", child], cwd=source_dir,
                 phase="native-evidence", cell_id="QRT-" + slug.upper(),
                 diagnostic_out=native_diag)
            raise AssertionError("R14_REAL_SYSTEMIC_CHILD_UNEXPECTED_PASS")

        def verified_pin(_root, _slug):
            return None
        visited = []
        def execute_real_at_third(root, slug):
            visited.append(slug)
            if len(visited) == 3:
                return real_systemic_case(root, slug)
            return {"cell_id": "QRT-" + slug.upper(), "status": "PASS",
                    "phase": "browser-navigation", "failure_code": None,
                    "candidate_round_trip": True}
        systemic_records, aborted = fanout_cases(
            execute_real_at_third, verified_pin,
            lambda slug, record: case_receipt(output, slug, record))
        assert aborted and len(visited) == 3
        third = systemic_records[2]
        assert third["cell_id"] == "QRT-RETRIEVE-D2"
        assert third["abort_kind"] == "SYSTEMIC_ABORT"
        assert third["assertion_type"] == "ContractError"
        assert third["failure_code"] == "SOURCE_CHANGED_SINCE_CONTRACT"
        assert all(item["status"] == "NOT_REACHED"
                   for item in systemic_records[3:])
        child_written = native_diag.read_text(encoding="utf-8")
        child_receipt = json.loads(child_written)
        assert child_receipt["failure_code"] == "SOURCE_CHANGED_SINCE_CONTRACT"
        assert child_receipt["assertion_type"] == "ContractError"
        assert child_receipt["candidate_21_case_result"] == "NOT_QUALIFIED"
        persisted = output.with_name(
            "prhead-overlay-retrieve-d2-CASE.json").read_text(encoding="utf-8")
        assert json.loads(persisted) == third
        assert secret not in persisted and secret not in child_written
        assert "Traceback" not in persisted and "Traceback" not in child_written
    print("R14 21-case diagnostic fanout + source-safe systemic class/code: PASS")


def source_safe_assertion(output: str) -> tuple[str, str]:
    """Return the child's REAL audited assertion class/code, never source text.

    Do not mistake a code occurring in original question text or a traceback
    argument for the assertion: match an exception terminator line only.
    The detail after the code may be private and is deliberately discarded.
    """
    import re
    matches = re.findall(
        r"(?m)^[ \t]*(?:qrt_intent_contract\.)?"
        r"(ContractError|AssertionError|RuntimeError):[ \t]*"
        r"([A-Z][A-Z0-9_]{6,})(?=[: \t]|$)",
        output,
    )
    for kind, code in reversed(matches):
        if code in SAFE_NATIVE_FAILURE_CODES:
            return kind, code
    for error_kind, safe in SAFE_FAILURE_FALLBACKS:
        if error_kind in output:
            return error_kind.removesuffix(":"), safe
    return "UNCLASSIFIED", "UNCLASSIFIED_SUBPROCESS_FAILURE"


def source_safe_failure_code(output: str) -> str:
    """Compatibility helper: sanitized code, NOT an arbitrary stdout token."""
    return source_safe_assertion(output)[1]


def diagnostic_self_test() -> None:
    """Synthetic source-safe child failure; verify actual on-disk JSON receipt."""
    from types import SimpleNamespace
    from unittest.mock import patch

    secret = "ORIGINAL_QUESTION_CONTENT_MUST_NOT_ESCAPE"
    sample = ("Traceback: " + secret +
              "\nContractError: CORE1B_GOLDEN_RECONSTRUCTION_DRIFT")
    classified = source_safe_failure_code(sample)
    assert classified == "CORE1B_GOLDEN_RECONSTRUCTION_DRIFT"
    assert source_safe_assertion(sample) == (
        "ContractError", "CORE1B_GOLDEN_RECONSTRUCTION_DRIFT")
    assert source_safe_assertion(
        "qrt_intent_contract.ContractError: "
        "CORE1B_GOLDEN_RECONSTRUCTION_DRIFT: " + secret) == (
            "ContractError", "CORE1B_GOLDEN_RECONSTRUCTION_DRIFT")
    # Lookalike modules and non-exception content must NEVER gain audited status.
    assert source_safe_failure_code(
        "some_other_module.ContractError: CORE1B_GOLDEN_RECONSTRUCTION_DRIFT") == (
            "CHILD_CONTRACT_ERROR_UNCLASSIFIED")
    assert source_safe_failure_code(
        "original page says CORE1B_GOLDEN_RECONSTRUCTION_DRIFT") == (
            "UNCLASSIFIED_SUBPROCESS_FAILURE")
    assert secret not in classified
    assert source_safe_failure_code(secret) == "UNCLASSIFIED_SUBPROCESS_FAILURE"
    assert source_safe_failure_code(
        "FileNotFoundError: " + secret) == "CHILD_FILE_NOT_FOUND"
    assert source_safe_failure_code(
        "ContractError: " + secret) == "CHILD_CONTRACT_ERROR_UNCLASSIFIED"

    with tempfile.TemporaryDirectory(prefix="r14-diagnostic-synthetic-") as td:
        receipt_path = Path(td) / "FAILURE-CODE.json"
        fake_child = SimpleNamespace(returncode=1, stdout=sample)
        with patch("subprocess.run", return_value=fake_child):
            try:
                call(["synthetic-not-executed"], phase="native-evidence",
                     cell_id="QRT-EXPLAIN-D3", diagnostic_out=receipt_path)
            except RuntimeError as err:
                caught = str(err)
                assert "CORE1B_GOLDEN_RECONSTRUCTION_DRIFT" in caught
            else:
                raise AssertionError("R14_SYNTHETIC_FAILURE_NOT_FAIL_CLOSED")

        written = receipt_path.read_text(encoding="utf-8")
        assert written.endswith("\\n") is False  # reject literal backslash+n
        assert written.endswith("\n")  # actual final U+000A whitespace
        receipt = json.loads(written)
        assert receipt["schema"] == "imo182-prhead-overlay-failure-code/v1"
        assert receipt["phase"] == "native-evidence"
        assert receipt["cell_id"] == "QRT-EXPLAIN-D3"
        assert receipt["failure_code"] == "CORE1B_GOLDEN_RECONSTRUCTION_DRIFT"
        assert receipt["assertion_type"] == "ContractError"
        assert receipt["exit_code"] == 1
        assert receipt["candidate_21_case_result"] == "NOT_QUALIFIED"
        assert receipt["native_return_counts_admissible"] is False
        assert receipt["no_source_text_or_raw_traceback"] is True
        assert secret not in written
        assert secret not in caught
        assert "ContractError: CORE1B_GOLDEN_RECONSTRUCTION_DRIFT" in caught
    # Exercise a REAL Python child and the repository's imported exception;
    # a mocked bare 'ContractError:' previously missed the qualified traceback.
    child_script = (
        "from qrt_intent_contract import ContractError\n"
        "raise ContractError('CORE1B_GOLDEN_RECONSTRUCTION_DRIFT: "
        + secret + "')\n"
    )
    child_command = [sys.executable, "-c", child_script]
    child_cwd = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(prefix="r14-imported-exception-") as td:
        # Verify this is the module-qualified Python traceback B observed.
        # Keep ALL raw stdout strictly in memory; do not print or write it.
        actual = subprocess.run(
            child_command, cwd=child_cwd, text=True, encoding="utf-8",
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        assert actual.returncode == 1
        assert ("qrt_intent_contract.ContractError: "
                "CORE1B_GOLDEN_RECONSTRUCTION_DRIFT: " + secret) in actual.stdout
        assert source_safe_assertion(actual.stdout) == (
            "ContractError", "CORE1B_GOLDEN_RECONSTRUCTION_DRIFT")
        imported_receipt = Path(td) / "IMPORTED-FAILURE-CODE.json"
        try:
            call(child_command, cwd=child_cwd, phase="native-evidence",
                 cell_id="QRT-EXPLAIN-D3", diagnostic_out=imported_receipt)
        except RuntimeError as error:
            imported_error = str(error)
        else:
            raise AssertionError("R14_IMPORTED_EXCEPTION_MUST_FAIL_CLOSED")
        imported_bytes = imported_receipt.read_text(encoding="utf-8")
        assert imported_bytes.endswith("\\n") is False
        assert imported_bytes.endswith("\n")
        imported = json.loads(imported_bytes)
        assert imported["schema"] == "imo182-prhead-overlay-failure-code/v1"
        assert imported["phase"] == "native-evidence"
        assert imported["cell_id"] == "QRT-EXPLAIN-D3"
        assert imported["assertion_type"] == "ContractError"
        assert imported["failure_code"] == "CORE1B_GOLDEN_RECONSTRUCTION_DRIFT"
        assert imported["exit_code"] == actual.returncode
        assert imported["candidate_21_case_result"] == "NOT_QUALIFIED"
        assert imported["native_return_counts_admissible"] is False
        assert imported["release"] == "HOLD"
        assert "ContractError: CORE1B_GOLDEN_RECONSTRUCTION_DRIFT" in imported_error
        assert secret not in imported_bytes
        assert secret not in imported_error
        assert "Traceback" not in imported_bytes
        assert "Traceback" not in imported_error
    verify_r14_source_isolation()
    fanout_self_test()
    cleanup_and_component_self_test()
    print("R14 source-safe classifier + on-disk JSON round-trip + "
          "real imported-ContractError subprocess: PASS")



def call(args: list[str], *, cwd: Path | None = None,
         phase: str | None = None, cell_id: str | None = None,
         diagnostic_out: Path | None = None) -> str:
    proc = subprocess.run(args, cwd=cwd, text=True, encoding="utf-8",
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if proc.returncode:
        # Do NOT print proc.stdout/stderr: it can contain source question content.
        assertion_kind, code = source_safe_assertion(proc.stdout)
        if phase is not None and diagnostic_out is not None:
            if phase not in {"renderer-build", "native-evidence",
                             "browser-navigation"} or cell_id not in {
                                 "QRT-" + slug.upper() for _root, slug in CASES
                             }:
                raise AssertionError("R14_DIAGNOSTIC_PHASE_OR_CELL_NOT_PINNED")
            receipt = {
                "schema": "imo182-prhead-overlay-failure-code/v1",
                "disposition": "FAIL_RUN_HOLD_ALL_21_NO_RENDERER_VERDICT",
                "phase": phase,
                "cell_id": cell_id,
                "failure_code": code,
                "assertion_type": assertion_kind,
                "exit_code": proc.returncode,
                "no_source_text_or_raw_traceback": True,
                "native_return_counts_admissible": False,
                "candidate_21_case_result": "NOT_QUALIFIED",
                "academic_accepted": 0,
                "owner_qrt_accepted": 0,
                "release": "HOLD",
            }
            diagnostic_out.parent.mkdir(parents=True, exist_ok=True)
            diagnostic_out.write_text(json.dumps(receipt, indent=2) + "\n",
                                      encoding="utf-8")
            print(f"R14_SOURCE_SAFE_ASSERTION phase={phase} cell={cell_id} "
                  f"{assertion_kind}: {code}; candidate 21 cases HOLD, no renderer verdict",
                  file=sys.stderr)
        if (phase in {"renderer-build", "native-evidence", "browser-navigation"}
                and cell_id in {"QRT-" + slug.upper() for _, slug in CASES}
                and code in CASE_LOCAL_FAILURE_CODES):
            raise CaseLocalFailure(phase, cell_id, assertion_kind, code)
        raise ChildProcessFailure(phase, assertion_kind, code)
    return proc.stdout.strip()


def blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()


def verify_old_r8_assignments() -> None:
    """Fail if our mapping drifts from the existing, source-held R8 case list."""
    import re
    content = WORKFLOW.read_text(encoding="utf-8")
    start = content.index("- name: R8 P2b click actual native role routes")
    stop = content.index("- name: R8 P2c inspect all 21", start)
    rows = re.findall(r'"(source-[a-z0-9-]+)[|]([a-z0-9-]+)"', content[start:stop])
    if tuple(rows) != CASES or len(set(c for _, c in CASES)) != 21:
        raise AssertionError("PR_HEAD_CASE_MAP_DRIFT_FROM_FROZEN_R8")


def original_source_is_pinned(source: Path, witness: dict) -> None:
    pin = witness["source_pin"]
    if call(["git", "-C", str(source), "rev-parse", "HEAD"]) != pin["commit"]:
        raise AssertionError("SOURCE_COMMIT_CHANGED")
    for path_key, blob_key in (("source_path", "source_blob"),
                               ("manifest_path", "manifest_blob")):
        path = source / pin[path_key]
        if not path.is_file() or blob_sha(path) != pin[blob_key]:
            raise AssertionError("SOURCE_MANIFEST_OR_PACKAGE_BLOB_CHANGED")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--self-test-diagnostic", action="store_true")
    args = parser.parse_args()
    if args.self_test_diagnostic:
        diagnostic_self_test()
        return
    if args.out is None:
        parser.error("--out is required outside synthetic diagnostic self-test")
    verify_old_r8_assignments()
    verify_r14_source_isolation()
    witnesses = json.loads((RECONCILIATION / "qrt-intent-witnesses-pilot.v1.json")
                           .read_text(encoding="utf-8"))
    by_cell = {w["cell_id"]: w for w in witnesses["witnesses"]}
    if len(by_cell) != 28:
        raise AssertionError("ORIGINAL_QRT_28_WITNESSES_DRIFT")
    renderer = RENDERER.resolve()
    head = call(["git", "rev-parse", "HEAD"])
    renderer_digest = hashlib.sha256(renderer.read_bytes()).hexdigest()
    reports: list[dict] = []
    args.out.parent.mkdir(parents=True, exist_ok=True)
    # Isolated git worktrees preserve source checkouts and all original R8
    # native HTML, per-page render receipts and frozen golden SHA receipts.
    held = set(by_cell) - {"QRT-" + slug.upper() for _, slug in CASES}
    if len(held) != 7:
        raise AssertionError("SOURCE_HELD_SEVEN_MUST_REMAIN_HELD")
    if len({r["cell_id"] for r in by_cell.values()}) != 28:
        raise AssertionError("ORIGINAL_QRT_28_WITNESS_DUPLICATION")
    with tempfile.TemporaryDirectory(prefix="imo182-prhead-", dir=str(args.out.parent.resolve())) as td:
        temp = Path(td)
        overlays: dict[str, tuple[Path, Path]] = {}

        def execute_case(root: str, slug: str) -> dict:
            cid = "QRT-" + slug.upper()
            witness = by_cell[cid]
            original = Path(r14_source_root(root, slug)).resolve()
            original_source_is_pinned(original, witness)
            expected_manifest = witness["source_pin"]["manifest_path"]
            if root not in overlays:
                shadow = temp / root
                call(["git", "-C", str(original), "worktree", "add",
                      "--detach", "-q", str(shadow), witness["source_pin"]["commit"]])
                overlays[root] = (original, shadow)
                (shadow / RENDERER).write_bytes(renderer.read_bytes())
            shadow = overlays[root][1]
            manifest = shadow / expected_manifest
            if blob_sha(manifest) != witness["source_pin"]["manifest_blob"]:
                raise AssertionError("OVERLAY_MANIFEST_BLOB_CHANGED")
            if blob_sha(shadow / witness["source_pin"]["source_path"]) != (
                witness["source_pin"]["source_blob"]
            ):
                raise AssertionError("OVERLAY_QUESTION_SOURCE_BLOB_CHANGED")
            selected = json.loads(manifest.read_text(encoding="utf-8"))["selection"]
            if selected["core2a"] != [witness["primary_question_id"]]:
                raise AssertionError("SELECTED_ORIGINAL_QUESTION_DRIFT")
            target = shadow / "build/imo182-qrt/prhead" / slug
            alternate = shadow / "build/imo182-qrt/prhead-repeat" / slug
            for where in (target, alternate):
                call([sys.executable, str(shadow / RENDERER), "build",
                      "--manifest", expected_manifest, "--out", str(where),
                      "--mode", "PAGES", "--reference", "--draft"], cwd=shadow,
                     phase="renderer-build", cell_id=cid,
                     diagnostic_out=args.out.with_name("prhead-overlay-" + slug + "-FAILURE-CODE.json"))
            candidate_contract = temp / (slug + "-prhead-native.json")
            try:
                call([sys.executable, str(RECONCILIATION / "qrt_intent_native_evidence.py"),
                      "--contract", str(Path("build/imo182-r8-intent") / (slug + ".json")),
                      "--source-root", str(shadow), "--native-output", str(target),
                      "--independent-rebuild", str(alternate), "--out", str(candidate_contract)],
                     phase="native-evidence", cell_id=cid,
                     diagnostic_out=args.out.with_name(
                         "prhead-overlay-" + slug + "-FAILURE-CODE.json"))
            except CaseLocalFailure as failure:
                if failure.code == "GOLDEN_COMPONENT_MISMATCH":
                    # Diagnostic-only: never modify renderer/immutable golden.
                    # Failure to inspect markers must not hide the native error.
                    try:
                        delta = source_safe_component_delta(shadow, target)
                        output = args.out.with_name(
                            "prhead-overlay-" + slug + "-COMPONENT-DIFF.json")
                        stage = output.with_name(output.name + ".tmp")
                        stage.write_text(json.dumps(delta, indent=2) + "\n",
                                         encoding="utf-8")
                        stage.replace(output)
                    except Exception:
                        pass
                raise
            nav_path = temp / (slug + "-prhead-navigation.json")
            call([sys.executable, str(RECONCILIATION / "qrt_intent_real_navigation.py"),
                  "--native-contract", str(candidate_contract),
                  "--source-root", str(shadow), "--native-output", str(target),
                  "--out", str(nav_path)],
                 phase="browser-navigation", cell_id=cid,
                 diagnostic_out=args.out.with_name("prhead-overlay-" + slug + "-FAILURE-CODE.json"))
            nav = json.loads(nav_path.read_text(encoding="utf-8"))
            journey = nav["postcommit_native_journey"]
            observed = journey["observed"]
            if nav["cell_id"] != cid or journey["source_question_id"] != witness["primary_question_id"]:
                raise AssertionError("PR_HEAD_SOURCE_QID_NOT_PINNED")
            if observed["independent_credit_claimed"]:
                raise AssertionError("ASSISTED_RETURN_FALSE_INDEPENDENT_CREDIT")
            record = {
                "cell_id": cid,
                "status": "PASS" if journey["technical_round_trip_complete"] else "FAIL",
                "phase": "browser-navigation",
                "failure_code": (None if journey["technical_round_trip_complete"]
                                 else "TECHNICAL_ROUND_TRIP_INCOMPLETE"),
                "source_commit": witness["source_pin"]["commit"],
                "original_source_blob": witness["source_pin"]["source_blob"],
                "original_manifest_blob": witness["source_pin"]["manifest_blob"],
                "renderer_head_sha": head,
                "renderer_sha256": renderer_digest,
                "page_sha256": json.loads(candidate_contract.read_text(
                    encoding="utf-8"))["native_evidence"]["roles"]["CORE2A"]["native_sha256"],
                "postcommit": {k: bool(observed[k]) for k in (
                    "attempt_blank_rejected", "nonempty_attempt_committed",
                    "precommit_solution_locked", "postcommit_context_link_present",
                    "context_link_is_pinned", "concept_reached", "concept_is_pinned",
                    "return_link_present", "return_link_is_pinned",
                    "same_question_reached", "attempt_text_restored",
                    "assistance_marked", "independent_credit_claimed")},
                "candidate_round_trip": bool(journey["technical_round_trip_complete"]),
                "finding_codes": list(journey["findings"]),
                "academic_acceptance": False,
                "owner_acceptance": False,
            }
            original_source_is_pinned(original, witness)
            return record
        def verify_case_pin(root: str, slug: str) -> None:
            original_source_is_pinned(Path(r14_source_root(root, slug)).resolve(),
                                      by_cell["QRT-" + slug.upper()])

        cleanup_failures: list[dict] = []
        try:
            reports, systemic_abort = fanout_cases(
                execute_case, verify_case_pin,
                lambda slug, record: case_receipt(args.out, slug, record))
        finally:
            # Each detached shadow is owned by its actual original checkout,
            # NOT necessarily its historical R8 case-root alias.
            cleanup_failures = cleanup_shadow_worktrees(overlays, call)
    assert set(r["cell_id"] for r in reports) | held == set(by_cell)
    failed = write_fanout_aggregate(
        args.out, reports, systemic_abort, cleanup_failures,
        held, head, renderer_digest)
    counts = {status: sum(r["status"] == status for r in reports)
              for status in ("PASS", "FAIL", "NOT_REACHED")}
    print(f"R14_SOURCE_SAFE_FANOUT pass={counts['PASS']} fail={counts['FAIL']} "
          f"not_reached={counts['NOT_REACHED']} held=7 "
          f"systemic_abort={systemic_abort} cleanup_failures={len(cleanup_failures)}; "
          "ALWAYS PROVISIONAL; academic/Owner HOLD")
    if failed:
        raise SystemExit("R14_FANOUT_FAILED_CLOSED; no native 21-case acceptance")

if __name__ == "__main__":
    main()
