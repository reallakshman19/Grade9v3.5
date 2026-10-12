#!/usr/bin/env python3
"""O1: compare a sole-renderer TEST Core2A page with the existing CANDIDATE golden.

This is structural/semantic technique evidence, NOT pixel parity, independently
reviewed mathematics, QRT acceptance, source custody or public release.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path


EXPECTED_ID = "Q-TEST-CORE2A-THREE-ADJACENT-PRODUCT-PROOF"
EXPECTED_BLUEPRINT = "BP-CORE2A-SUPPORTED-APPLICATION@1.1.0"
SLOTS = ("identity", "attempt", "support", "reasoning")
ESSENTIAL = ("stem", "reasoning_route", "independent_check")


class Anatomy(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slots = []
        self.blocks = []
        self.units = []
        self.blueprints = []
        self.roles = []
        self.attempts = 0
        self.hint_ladders = 0
        self.protected_reveals = 0
        self.protected_payloads = 0
        self.next_hint_buttons = 0

    def handle_starttag(self, tag, pairs):
        a = dict(pairs)
        for name, destination in (
            ("data-blueprint-slot", self.slots),
            ("data-g9-block", self.blocks),
            ("data-g9-unit", self.units),
            ("data-blueprint-ref", self.blueprints),
            ("data-g9-role", self.roles),
        ):
            if a.get(name):
                destination.append(a[name])
        self.attempts += int("data-g9-attempt-box" in a)
        self.hint_ladders += int("data-g9-ladder" in a)
        self.protected_reveals += int("data-requires-attempt" in a)
        self.protected_payloads += int("data-g9-payload" in a)
        self.next_hint_buttons += int("data-g9-next-rung" in a)


def anatomy(path: Path) -> Anatomy:
    parser = Anatomy()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def verify(rendered: Path, golden: Path, manifest_path: Path, report: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    receipt = json.loads((rendered.parent / "render-receipt.json").read_text(encoding="utf-8"))
    package = json.loads(Path(
        "TEST/imo-research/pilots/core1a-render-qualified-divisibility.v1.json"
    ).read_text(encoding="utf-8"))
    question = next(q for q in package["questions"] if q["id"] == EXPECTED_ID)
    qrt = json.loads(Path("TEST/imo-research/verification/qrt-proposed-coverage.v1.json").read_text())
    actual, reference = anatomy(rendered), anatomy(golden)
    checks = {
        "TEST manifest, one Core2A output, zero Core2 source questions":
            manifest["subject"] == "TEST" and manifest["output_roles"] == ["CORE2A"]
            and manifest["selection"]["core2"] == []
            and manifest["selection"]["core2a"] == [EXPECTED_ID],
        "Same sole-renderer Core2A blueprint as golden":
            actual.blueprints == reference.blueprints == [EXPECTED_BLUEPRINT],
        "Same ordered blueprint slots as golden":
            actual.slots == reference.slots == list(SLOTS),
        "Selected authored question is actually on learner page":
            EXPECTED_ID in actual.units,
        "Actual Core2A task, hint and gated working":
            actual.attempts >= 1 and actual.hint_ladders >= 1
            and actual.next_hint_buttons >= 1 and actual.protected_reveals >= 1
            and actual.protected_payloads >= 1,
        "T05 progressive support and T07 independent check on both":
            all(name in actual.blocks and name in reference.blocks for name in ESSENTIAL),
        "QRT candidate remains authored and unaccepted":
            question["origin"] == "AUTHORED"
            and question["extensions"]["grade9v3:cognitive_demand"]["primary"] == "JUSTIFY"
            and question["difficulty"]["band"] == "D2"
            and qrt["accepted_coverage_numerator"] == 0
            and qrt["accepted_coverage_denominator"] == 28,
        "Canonical crux bound to a real reasoning step":
            any(move["id"] == question["answer"]["crux_move_ref"]
                for move in question["answer"]["reasoning_route"]),
        "Reference-depth gaps honestly reported":
            receipt["held_to"] == "REFERENCE" and receipt["output_roles"] == ["CORE2A"],
    }
    summary = {
        "schema": "imo-182-core2a-golden-structural-comparison/v1",
        "outcome": "O1",
        "product_id": manifest["product_id"],
        "role": "CORE2A",
        "blueprint": EXPECTED_BLUEPRINT,
        "golden_status": "CANDIDATE_NOT_OWNER_BLESSED",
        "qrt_cell": "QRT-JUSTIFY-D2",
        "qrt_status": "PROPOSED_NOT_ACCEPTED",
        "question_origin": "AUTHORED",
        "real_learner_inputs": "NOT_AVAILABLE",
        "mathematics_human_review": "NOT_RUN",
        "owner_visual_a4": "NOT_RUN",
        "pixel_parity": "NOT_RUN",
        "core1a_repair_link": "NOT_RENDERED_IN_THIS_CORE2A_ONLY_PRODUCT",
        "page_sha256": hashlib.sha256(rendered.read_bytes()).hexdigest(),
        "golden_sha256": hashlib.sha256(golden.read_bytes()).hexdigest(),
        "render_digest": receipt["digest"],
        "renderer_gap_count": len(receipt["gaps"]),
        "renderer_gaps": receipt["gaps"],
        "slot_sequence": actual.slots,
        "golden_slot_sequence": reference.slots,
        "blocks_missing_vs_golden": sorted(set(reference.blocks) - set(actual.blocks)),
        "blocks_extra_vs_golden": sorted(set(actual.blocks) - set(reference.blocks)),
        "checks": checks,
        "structural_alignment": "PASS" if all(checks.values()) else "FAIL",
        "full_golden_acceptance": "NOT_GRANTED",
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    for check, result in checks.items():
        print(("PASS" if result else "FAIL") + " | " + check)
    print("renderer gaps:", len(receipt["gaps"]))
    print("golden candidate comparison:", report)
    if not all(checks.values()):
        raise SystemExit(1)
    return summary


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--rendered", type=Path, required=True)
    p.add_argument("--golden", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    a = p.parse_args()
    verify(a.rendered, a.golden, a.manifest, a.report)


if __name__ == "__main__":
    main()
