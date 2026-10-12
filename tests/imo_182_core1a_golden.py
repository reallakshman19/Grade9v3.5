#!/usr/bin/env python3
"""IMO #182 O1: inspect a real sole-renderer Core1A TEST page against the CANDIDATE golden.

Checks published authoring technique/structural affordances, not literal text, screenshot parity,
independent mathematics, real learner success, Owner golden blessing, QRT acceptance or release.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import json

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "TEST/products/core1a-divisibility-render-maturity.manifest.json"
PACKAGE = ROOT / "TEST/imo-research/pilots/core1a-render-qualified-divisibility.v1.json"
REGISTRY = ROOT / "Shared/web/interactive-page-blueprints.v1.json"
ACCEPTED_QRT = ROOT / "TEST/imo-research/verification/qrt-proposed-coverage.v1.json"
EXPECTED_ROLE = "CORE1A"
EXPECTED_REF = "BP-CORE1A-CONSTRUCTION@1.8.0"
UNIT = "MIC-TEST-CORE1A-QUAL-G9-CONSECUTIVE-FACTOR-INVARIANTS"
CORE2A_QUESTION = "Q-TEST-CORE2A-THREE-ADJACENT-PRODUCT-PROOF"


class Anatomy(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slots = []
        self.components = []
        self.blocks = []
        self.units = []
        self.role = []
        self.blueprint = []
        self.svg_stages = []
        self.figures = 0
        self.exit_controls = 0
        self.reveals = 0

    def handle_starttag(self, tag, pairs):
        a = dict(pairs)
        for key, dst in (
            ("data-blueprint-slot", self.slots),
            ("data-g9-component", self.components),
            ("data-g9-block", self.blocks),
            ("data-g9-unit", self.units),
            ("data-g9-role", self.role),
            ("data-blueprint-ref", self.blueprint),
            ("data-g9-stage-id", self.svg_stages),
        ):
            if a.get(key):
                dst.append(a[key])
        if tag == "figure" and "data-g9-figure" in a:
            self.figures += 1
        if "data-g9-attempt-box" in a:
            self.exit_controls += 1
        if "data-g9-reveal" in a:
            self.reveals += 1


def read_html(path):
    obj = Anatomy()
    obj.feed(path.read_text(encoding="utf-8"))
    return obj


def digest(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--product", required=True, type=Path)
    cli.add_argument("--golden", required=True, type=Path)
    cli.add_argument("--report", required=True, type=Path)
    args = cli.parse_args()

    product, golden = args.product, args.golden
    rendered, fixture = product / "core1a.html", golden / "core1a.html"
    actual, reference = read_html(rendered), read_html(fixture)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    package = json.loads(PACKAGE.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    cells = json.loads(ACCEPTED_QRT.read_text(encoding="utf-8"))
    deploy = json.loads((product / "deploy-receipt.json").read_text(encoding="utf-8"))
    printer = json.loads((product / "print-receipt.json").read_text(encoding="utf-8"))
    golden_receipt = json.loads((golden / "render-receipt.json").read_text(encoding="utf-8"))
    bp = next(bp for bp in registry["blueprints"] if EXPECTED_ROLE in bp["core_roles"])
    required = {c["id"] for c in bp["components"] if c["level"] == "REQUIRED"}
    slots = [row["id"] for row in bp["slots"]]

    matching_pdf = next((row for row in printer["pages"] if row["page"] == "core1a.html"), None)
    pdf = product / "core1a.pdf"
    pdf_pages = []
    if pdf.is_file():
        pdf_pages = [" ".join((page.extract_text() or "").split()) for page in PdfReader(pdf).pages]

    checks = {
        "Existing authored Core1A manifest only (zero authentic Core2)":
            manifest["subject"] == "TEST" and manifest["output_roles"] == [EXPECTED_ROLE]
            and manifest["selection"]["microtopics"] == [UNIT] and not manifest["selection"]["core2"],
        "Exactly the registered Core1A blueprint on both pages":
            actual.blueprint == reference.blueprint == [EXPECTED_REF],
        "Same blueprint-required slot order in actual, golden and registry":
            actual.slots == reference.slots == slots,
        "All registered REQUIRED components in both real pages":
            required <= set(actual.components) and required <= set(reference.components),
        "Actual constructed concept and staged authored mathematical figure":
            UNIT in actual.units and actual.figures >= 1 and len(actual.svg_stages) >= 3,
        "Worked construction and genuine independent exit attempt rendered":
            "CONSTRUCTION_STEPS" in actual.components and "EXIT_RECALL" in actual.components
            and actual.exit_controls >= 1 and actual.reveals >= 1,
        "Existing TEST product receipt: draft only, no Owner acceptance":
            deploy.get("subject") == "TEST" and deploy.get("accepted") is False
            and deploy.get("draft") is True and deploy.get("roles") == [EXPECTED_ROLE],
        "No unknown authored reference-depth gaps in candidate or golden":
            deploy.get("gap_count") == 0 and golden_receipt.get("gaps") == [],
        "Same-page renderer-connected learner A4 print, hash-bound":
            printer.get("mode") == "LEARNER_PDF" and matching_pdf is not None
            and pdf.is_file() and pdf.stat().st_size > 1000
            and matching_pdf.get("pdf_digest") == digest(pdf)
            and bool(matching_pdf.get("page_digest")),
        "Math stage headings present in the generated PDF":
            bool(pdf_pages) and all(any(mark in sheet for sheet in pdf_pages)
                for mark in ("Parity guarantee", "Remainders modulo 3", "Combine valid factors")),
        "Authored QRT candidate stays proposed and cells unaccepted":
            cells.get("accepted_coverage_numerator") == 0
            and cells.get("accepted_coverage_denominator") == 28
            and next(q for q in package["questions"] if q["id"] == CORE2A_QUESTION)["origin"] == "AUTHORED",
    }

    output = {
        "schema": "imo-182-core1a-candidate-golden-and-print/v1",
        "task": "182-T2",
        "outcome": "O1",
        "source": "EXISTING_AUTHORED_TEST_PACKAGE",
        "blueprint": EXPECTED_REF,
        "golden_status": "CANDIDATE_NOT_OWNER_BLESSED",
        "golden_comparison": "TECHNIQUE_STRUCTURAL_ONLY_NOT_PIXEL_EQUIVALENCE",
        "output_not_published": True,
        "qrt_cell_served_by_adjacent_core2a": "QRT-JUSTIFY-D2_PROPOSED",
        "qrt_accepted": False,
        "real_learner_input": "NOT_AVAILABLE",
        "owner_a4_visual_acceptance": "NOT_RUN",
        "html_sha256": digest(rendered),
        "golden_html_sha256": digest(fixture),
        "role_pdf_sha256": digest(pdf) if pdf.is_file() else None,
        "same_page_print_receipt_found": matching_pdf is not None,
        "a4_pdf_page_count": len(pdf_pages),
        "blueprint_slots": actual.slots,
        "golden_slots": reference.slots,
        "registered_required_components": sorted(required),
        "actual_components": sorted(set(actual.components)),
        "golden_components": sorted(set(reference.components)),
        "missing_required": sorted(required - set(actual.components)),
        "missing_golden_components": sorted(set(reference.components) - set(actual.components)),
        "new_non_golden_components": sorted(set(actual.components) - set(reference.components)),
        "render_gap_count": deploy.get("gap_count"),
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "technical_result": "PASS" if all(checks.values()) else "FAIL",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(("PASS" if passed else "FAIL") + " | " + name)
    print(f"candidate golden comparison: {output['checks_passed']}/{output['checks_total']}, gaps={output['render_gap_count']}")
    print("Owner visual and QRT decision: NOT_RUN / NOT_ACCEPTED")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
