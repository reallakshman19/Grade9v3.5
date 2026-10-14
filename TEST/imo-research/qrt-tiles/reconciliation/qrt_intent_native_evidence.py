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


def attach_native_contract(
    contract: dict, source_root: Path, output: Path
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
    receipt_path = output / "render-receipt.json"
    ensure(receipt_path.is_file(), "RENDER_RECEIPT_MISSING")
    receipt = read_json(receipt_path)
    ensure(receipt.get("renderer") == "render_core/2" and
           receipt.get("mode") == "PAGES" and
           receipt.get("held_to") == "REFERENCE" and
           receipt.get("gaps") == [],
           "RENDERER_AUTHORITY_OR_GAPS")
    index = output / "index.html"
    ensure(index.is_file() and
           receipt.get("page_sha256", {}).get("index.html") == sha256(index),
           "INDEX_SHA_NOT_RECEIPT")
    proof = {}
    for role in ROLES:
        filename = role.lower() + ".html"
        page = output / filename
        ensure(page.is_file(), "MISSING_NATIVE_ROLE", filename)
        digest = sha256(page)
        ensure(receipt["page_sha256"].get(filename) == digest,
               "NATIVE_PAGE_SHA_NOT_RECEIPT", filename)
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
            "receipt_sha256_match": True,
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
        "index_sha256": sha256(index),
        "roles": proof,
        "golden_immutability": "FIVE_SNAPSHOT_SHAS_CONFIRMED",
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
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    report = attach_native_contract(
        read_json(args.contract), args.source_root, args.native_output
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print(f"{report['cell_id']}: P1 five registered roles native SHA+"
          " frozen golden structure PASS, learner QRT semantic NOT_RUN; "
          "academic+Owner HOLD")


if __name__ == "__main__":
    main()
