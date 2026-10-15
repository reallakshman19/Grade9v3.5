#!/usr/bin/env python3
"""IMO #182 R8 P1: native five-role structural evidence adapter for QRT contracts.

Runs after Shared/tools/render_core.py. No second rendering authority or
academic semantic classifier. Distinguishes verified structural proof from
mathematical correctness, live browser gates, human QRT review and acceptance.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path

from qrt_intent_contract import (
    BP, ROLES, ContractError, blob_hash, ensure, read_json, resolve_under, sha256
)

LOCK_BLOB = "888678554c41257e6d96c802f0009983ccbb5328"
GOLDEN = "G-IMO-G9-FIVE-CORE-20261012"


class NativeStructure(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slots = []
        self.components = []
        self.blocks = []
        self.blueprints = []
        self.roles = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        for key, target in (
            ("data-blueprint-slot", self.slots),
            ("data-g9-component", self.components),
            ("data-g9-block", self.blocks),
            ("data-blueprint-ref", self.blueprints),
            ("data-g9-role", self.roles),
        ):
            if data.get(key):
                target.append(data[key])


def parse(path: Path) -> NativeStructure:
    parser = NativeStructure()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser



# Owner AB-R14-PRACTICE: never mutate or displace the historical R8 golden.
# R14 alone may explicitly request this separately locked structural v2.
R14_GOLDEN = "G-IMO-G9-FIVE-CORE-20261012-v2-PRACTICE"
R14_GOLDEN_RELATIVE = Path("golden/units/G-IMO-G9-FIVE-CORE-20261012-v2-PRACTICE")
R14_GOLDEN_LOCK_BLOB = "53870580200de9f08f9f2ebe0a21ecc46fcf02f5"
R14_MARKER_NODE = b'<div data-g9-component="PRACTICE_LINKS"></div>'
R14_TRANSITIONS_ANCHOR = b'data-g9-component="LEARNING_TRANSITIONS"'


def verify_only_authorized_practice_delta(old: bytes, new: bytes) -> None:
    """Full byte-level structural oracle: ONE insertion, no other mutation."""
    ensure(old.count(R14_TRANSITIONS_ANCHOR) == 1 and
           old.count(R14_MARKER_NODE) == 0, "R14_GOLDEN_BASE_MARKERS_DRIFT")
    anchor = old.index(R14_TRANSITIONS_ANCHOR)
    tag_start = old.rfind(b"<div", 0, anchor)
    ensure(tag_start >= 0 and anchor - tag_start < 230,
           "R14_GOLDEN_INSERTION_ANCHOR_DRIFT")
    expected = old[:tag_start] + R14_MARKER_NODE + old[tag_start:]
    ensure(new == expected, "R14_GOLDEN_ONLY_PRACTICE_LINKS_PERMITTED")


def verify_r14_versioned_golden(source_root: Path, versioned_root: Path) -> dict:
    """Check BOTH locks and every role; fail closed on any unapproved delta."""
    legacy_lock = resolve_under(
        source_root, "golden/units/" + GOLDEN + "/snapshot-lock.json")
    legacy_root = legacy_lock.parent
    ensure(blob_hash(legacy_lock) == LOCK_BLOB,
           "IMMUTABLE_GOLDEN_LOCK_DRIFT")
    ensure(versioned_root.resolve() == R14_GOLDEN_RELATIVE.resolve(),
           "R14_GOLDEN_VERSION_NOT_EXPLICIT")
    new_lock_path = versioned_root / "snapshot-lock.json"
    ensure(blob_hash(new_lock_path) == R14_GOLDEN_LOCK_BLOB,
           "R14_GOLDEN_V2_LOCK_DRIFT")
    original = read_json(legacy_lock)
    proposed = read_json(new_lock_path)
    ensure(original.get("fixture_id") == GOLDEN and
           proposed.get("fixture_id") == R14_GOLDEN and
           proposed.get("base_fixture_id") == GOLDEN and
           proposed.get("base_fixture_lock_git_blob_sha") == LOCK_BLOB and
           proposed.get("only_allowed_delta") == {
               "role": "CORE1A", "component": "PRACTICE_LINKS",
               "ordinal_zero_based": 11,
               "markup": R14_MARKER_NODE.decode("utf-8")
           } and
           proposed.get("academic_accepted") == 0 and
           proposed.get("owner_qrt_accepted") == 0 and
           proposed.get("release") == "HOLD",
           "R14_GOLDEN_VERSION_AUTHORITY_DRIFT")
    older = original["snapshots"]
    newer = proposed["snapshots"]
    ensure(len(older) == len(newer) == 5 and
           {item["role"] for item in older} ==
           {item["role"] for item in newer} == set(ROLES),
           "R14_GOLDEN_ROLE_SET_DRIFT")
    for role in ROLES:
        old_rec = next(x for x in older if x["role"] == role)
        new_rec = next(x for x in newer if x["role"] == role)
        path = "snapshots/" + role.lower() + ".html"
        ensure(old_rec["path"] == new_rec["path"] == path,
               "R14_GOLDEN_SNAPSHOT_PATH_DRIFT")
        old_snapshot = legacy_root / path
        new_snapshot = versioned_root / path
        ensure(sha256(old_snapshot) == old_rec["sha256"] and
               sha256(new_snapshot) == new_rec["sha256"] and
               blob_hash(new_snapshot) == new_rec["git_blob_sha"],
               "R14_GOLDEN_SNAPSHOT_BYTES_DRIFT")
        old_bytes, new_bytes = old_snapshot.read_bytes(), new_snapshot.read_bytes()
        if role == "CORE1A":
            verify_only_authorized_practice_delta(old_bytes, new_bytes)
            old_ids = parse(old_snapshot).components
            new_ids = parse(new_snapshot).components
            ensure(len(old_ids) == 12 and
                   new_ids == old_ids[:11] + ["PRACTICE_LINKS"] + old_ids[11:],
                   "R14_GOLDEN_COMPONENT_DELTA_DRIFT")
        else:
            ensure(new_bytes == old_bytes and
                   new_rec["sha256"] == old_rec["sha256"] and
                   new_rec["git_blob_sha"] == old_rec["git_blob_sha"],
                   "R14_GOLDEN_NON_CORE1A_CHANGED")
    return proposed


def attach_native_contract(
    contract: dict, source_root: Path, output: Path,
    independent_rebuild: Path | None = None,
    r14_golden_dir: Path | None = None
) -> dict:
    """Reject stale bytes, compare source pages to frozen snapshots, leave W HOLD."""
    contract = copy.deepcopy(contract)
    ensure(contract["technical_contract"] == "VALIDATED_PROPOSAL" and
           contract["semantic_review"] == "HOLD_REVIEW_REQUIRED",
           "UNVALIDATED_QRT_CONTRACT")
    provenance = contract["provenance"]
    ensure(blob_hash(resolve_under(source_root, provenance["source_path"])) ==
           provenance["source_git_blob"],
           "SOURCE_CHANGED_SINCE_CONTRACT")
    ensure(blob_hash(resolve_under(source_root, provenance["manifest_path"])) ==
           provenance["manifest_git_blob"],
           "MANIFEST_CHANGED_SINCE_CONTRACT")
    reg_path = resolve_under(source_root,
                             "Shared/web/interactive-page-blueprints.v1.json")
    lock_path = resolve_under(source_root,
                              "golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshot-lock.json")
    ensure(blob_hash(reg_path) == provenance["registry_git_blob"],
           "REGISTRY_CHANGED_SINCE_CONTRACT")
    ensure(blob_hash(lock_path) == LOCK_BLOB,
           "IMMUTABLE_GOLDEN_LOCK_DRIFT")
    golden_dir = lock_path.parent
    frozen = read_json(lock_path)
    ensure(frozen["fixture_id"] == GOLDEN,
           "WRONG_FROZEN_GOLDEN")
    if r14_golden_dir is not None:
        # Historical path is validated above and remains the R8 default.
        frozen = verify_r14_versioned_golden(source_root, r14_golden_dir)
        golden_dir = r14_golden_dir
    receipt_path = output / "render-receipt.json"
    ensure(receipt_path.is_file(), "RENDER_RECEIPT_MISSING")
    receipt = read_json(receipt_path)
    ensure(receipt.get("renderer") == "render_core/2" and
           receipt.get("mode") == "PAGES" and
           receipt.get("held_to") == "REFERENCE" and
           receipt.get("gaps") == [],
           "RENDERER_AUTHORITY_OR_GAPS")
    all_pages = [r.lower() + ".html" for r in ROLES] + ["index.html"]
    ensure(receipt.get("pages") == all_pages and
           receipt.get("output_roles") == list(ROLES),
           "RENDER_RECEIPT_ROLES_OR_PAGES")
    page_shas = receipt.get("page_sha256")
    has_receipt_sha = isinstance(page_shas, dict)
    if has_receipt_sha:
        ensure(set(page_shas) == set(all_pages),
               "RENDER_RECEIPT_SHA_SET_DRIFT")
    else:
        # Certain earlier *exact pinned* authors use an older renderer receipt
        # that lists pages but does not record per-page hashes. Never claim
        # receipt-to-page SHA match. Require byte-identical independent rerender.
        ensure(page_shas is None, "MALFORMED_RENDER_RECEIPT_SHAS")
        ensure(independent_rebuild is not None,
               "LEGACY_RECEIPT_REQUIRES_INDEPENDENT_RERENDER")
        repeat_receipt = read_json(
            independent_rebuild / "render-receipt.json")
        for field in ("renderer", "mode", "held_to", "gaps",
                      "pages", "output_roles", "digest", "semantic_digest"):
            ensure(receipt.get(field) == repeat_receipt.get(field),
                   "INDEPENDENT_RECEIPT_CHANGED", field)
    index = output / "index.html"
    ensure(index.is_file(), "INDEX_MISSING")
    if has_receipt_sha:
        ensure(page_shas.get("index.html") == sha256(index),
               "INDEX_SHA_NOT_RECEIPT")
    else:
        repeated_index = independent_rebuild / "index.html"
        ensure(repeated_index.is_file() and
               sha256(repeated_index) == sha256(index),
               "LEGACY_INDEX_NONDETERMINISTIC")
    proof = {}
    for role in ROLES:
        filename = role.lower() + ".html"
        page = output / filename
        ensure(page.is_file(), "MISSING_NATIVE_ROLE", filename)
        digest = sha256(page)
        if has_receipt_sha:
            ensure(page_shas.get(filename) == digest,
                   "NATIVE_PAGE_SHA_NOT_RECEIPT", filename)
        else:
            repeated_page = independent_rebuild / filename
            ensure(repeated_page.is_file() and
                   sha256(repeated_page) == digest,
                   "LEGACY_CORE_NONDETERMINISTIC", filename)
        frozen_records = [x for x in frozen["snapshots"]
                          if x["role"] == role]
        ensure(len(frozen_records) == 1,
               "GOLDEN_ROLE_NOT_UNIQUE", role)
        frozen_rec = frozen_records[0]
        frozen_path = resolve_under(golden_dir, frozen_rec["path"])
        ensure(sha256(frozen_path) == frozen_rec["sha256"],
               "GOLDEN_SNAPSHOT_BYTES_DRIFT", role)
        real = parse(page)
        locked = parse(frozen_path)
        ensure(real.roles[:1] == locked.roles[:1] == [role] and
               real.blueprints == locked.blueprints == [BP[role]],
               "ROLE_BLUEPRINT_MISMATCH", role)
        ensure(real.slots == locked.slots and len(real.slots) >= 2,
               "GOLDEN_SLOT_MISMATCH", role)
        ensure(real.components == locked.components,
               "GOLDEN_COMPONENT_MISMATCH", role)
        # Frozen order is a structural observation, not a guarantee of
        # teaching semantics: nonidentical blocks remain contextual.
        is_exact = real.blocks == locked.blocks
        if role == "CORE1B":
            ensure(is_exact and len(real.blocks) == 13,
                   "CORE1B_GOLDEN_RECONSTRUCTION_DRIFT")
        proof[role] = {
            "native_sha256": digest,
            "receipt_sha256_match": True if has_receipt_sha else None,
            "independent_same_renderer_rebuild_sha_match":
                True if not has_receipt_sha else None,
            "frozen_golden_sha256": frozen_rec["sha256"],
            "frozen_golden_sha256_match": True,
            "blueprint": BP[role],
            "slots": "MATCH",
            "components": "MATCH",
            "blocks": "MATCH_EXACT" if is_exact else "CONTEXTUAL_DIFFERENCE",
            "browser_attempt_gates": "NOT_RUN",
            "independent_math": "NOT_RUN",
            "semantic_QRT": "NOT_RUN",
            "cross_core_W": "NOT_RUN"
        }
        # Do not collapse a structural PASS into a complete engineering PASS.
        contract["roles"][role]["engineering_native_structure"] = "PASS"
        contract["roles"][role]["native_sha256"] = digest
        contract["roles"][role]["golden_structural_evidence"] = {
            "slots": "MATCH", "components": "MATCH",
            "blocks": proof[role]["blocks"]
        }
        contract["roles"][role]["engineering"] = "NOT_RUN"
        contract["roles"][role]["semantic"] = "NOT_RUN"
    contract["native_evidence"] = {
        "scope": "NATIVE_STRUCTURE_ONLY",
        "renderer": "Shared/tools/render_core.py",
        "receipt_sha256": sha256(receipt_path),
        "page_sha_authority": (
            "EXACT_NATIVE_RENDER_RECEIPT" if has_receipt_sha else
            "SAME_PINNED_SOLE_RENDERER_INDEPENDENT_BYTE_IDENTICAL_RERENDER"
        ),
        "receipt_contains_page_sha256": has_receipt_sha,
        "index_sha256": sha256(index),
        "roles": proof,
        "golden_immutability": "FIVE_SNAPSHOT_SHAS_CONFIRMED",
        "golden_fixture_id": R14_GOLDEN if r14_golden_dir is not None else GOLDEN,
        "all_role_structure": "PASS",
        "independent_math": "NOT_RUN",
        "browser_and_AX": "NOT_RUN",
        "cross_core_W": "NOT_RUN",
        "academic_accepted": False,
        "owner_accepted": False
    }
    contract["provenance"]["golden_verification"] = (
        "FIVE_ROLE_SHA_AND_STRUCTURAL_MATCH"
    )
    return contract


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--native-output", required=True, type=Path)
    parser.add_argument("--independent-rebuild", type=Path,
                        help="Required for legacy pinned receipts without per-page hashes")
    parser.add_argument("--r14-golden-dir", type=Path,
                        help="Owner AB-R14-PRACTICE explicit review-only v2; R8 defaults to old lock")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    report = attach_native_contract(
        read_json(args.contract), args.source_root, args.native_output,
        args.independent_rebuild, args.r14_golden_dir
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print(f"{report['cell_id']}: P1 five registered roles native SHA+"
          " frozen golden structure PASS, learner QRT semantic NOT_RUN; "
          "academic+Owner HOLD")


if __name__ == "__main__":
    main()
