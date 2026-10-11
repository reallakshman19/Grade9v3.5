#!/usr/bin/env python3
"""Track A #173: SHA-bound real HTML vs two *candidate* golden technique checks.

Compares semantic/behavioral criteria, not byte-equivalence between different content.
Screenshot/human/math admission gates remain explicitly NOT_RUN / NOT_ACCEPTED.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from Shared.tools import render_core

ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "golden/units"
BASELINE = "778eb35a70517a46108ad0a5dc01dfc89f61c0e3"
PAIRS = {
    "five_120": ("imo-g9-track-a-four-role-five-120.manifest.json",
                 "Q-TEST-IMO-164-FIVE-CONSECUTIVE-120", "gcd(24,5)=1"),
    "boundary_12": ("imo-g9-track-a-four-role-boundary-12.manifest.json",
                    "Q-TEST-IMO-164-TRIPLE-12-IFF-BOUNDARY", "n mod 4 != 1"),
}
EXPECTED_ROLES = ["CORE2A", "CORE1A", "CORE1B", "CORE2B"]


class Visible(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.excluded = []
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("template", "script", "style"):
            self.excluded.append(tag)

    def handle_endtag(self, tag):
        if self.excluded and tag == self.excluded[-1]:
            self.excluded.pop()

    def handle_data(self, data):
        if not self.excluded:
            self.parts.append(data)

    def text(self):
        return " ".join(self.parts)


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def measure_html(page: str) -> dict:
    return {
        "articles": len(re.findall(r"<article\b", page)),
        "main_regions": len(re.findall(r"<main\b", page)),
        "attempt_boxes": len(re.findall(r"<div\b[^>]*data-g9-attempt-box", page)),
        "locked_disclosures": len(re.findall(r"<details\b[^>]*data-requires-attempt", page)),
        "pre_attempt_figures": len(re.findall(
            r'<figure\b[^>]*data-g9-stage="PRE_ATTEMPT"', page)),
        "inert_payloads": len(re.findall(r"<template\b[^>]*data-g9-payload=", page)),
        "figure_instances": len(re.findall(r"<figure\b[^>]*data-g9-figure", page)),
        "landmark_navs": len(re.findall(r"<nav\b", page)),
    }



# Compare real, rendered candidate anatomy with the features shared by BOTH
# candidate exemplars; content and exact count equality are not promised.
# This is a structural crosswalk, not a CSS layout, screenshot or AT verdict.
GOLDEN_ANATOMY_METRICS = (
    "articles", "main_regions", "attempt_boxes", "locked_disclosures",
    "inert_payloads", "figure_instances", "landmark_navs",
)


def golden_role_crosswalk(goldens: dict, role: str, candidate_html: str) -> dict:
    page = role.lower() + ".html"
    references = {gid: data["pages"].get(page) for gid, data in goldens.items()}
    measured = measure_html(candidate_html)
    unavailable = sorted(gid for gid, features in references.items() if features is None)
    shared_present = [
        metric for metric in GOLDEN_ANATOMY_METRICS
        if not unavailable and all(reference[metric] > 0 for reference in references.values())
    ]
    missing = [metric for metric in shared_present if measured[metric] == 0]
    return {
        "role": role,
        "actual": measured,
        "golden_refs": references,
        "required_common_present": shared_present,
        "missing_common_present": missing,
        "missing_golden_role_pages": unavailable,
        "passes": not unavailable and bool(shared_present) and not missing,
        "comparison_limit": "Shared nonzero rendered HTML features only; NOT visual/zoom/AT acceptance",
    }


def score(rows: list, criterion: str, expectation: str, good: bool,
          measured, golden: str = "G-MATH-LINEAR-CONSTRAINT") -> None:
    rows.append({
        "criterion": criterion, "golden_method_reference": golden,
        "expectation": expectation, "observed": measured,
        "status": "PASS" if good else "FAIL",
    })


def evaluate(head: str) -> dict:
    goldens = {}
    for gid in ("G-MATH-LINEAR-CONSTRAINT", "G-CORE2-R2"):
        manifest = GOLD / gid / "manifest.json"
        pages, gaps, rendered_digest, _, _ = render_core.build_report(manifest, "PAGES")
        assert not gaps and len(pages) == 7, (gid, gaps, sorted(pages))
        goldens[gid] = {
            "manifest_sha256": digest(manifest),
            "render_digest": rendered_digest,
            "pages": {name: measure_html(body) for name, body in pages.items()},
            "status": "CANDIDATE_NOT_OWNER_BLESSED",
        }
    outcomes = []
    for key, (manifest_name, transfer_id, secret) in PAIRS.items():
        manifest_path = ROOT / "TEST/products" / manifest_name
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        pages, gaps, render_digest, advisories, waivers = render_core.build_report(
            manifest_path, "PAGES", held_to="REFERENCE")
        rows = []
        actual_pages = sorted(pages)
        expected_pages = sorted(["index.html"] + [r.lower() + ".html" for r in EXPECTED_ROLES])
        score(rows, "ROLE_PAGES", "four ordered role pages plus index", actual_pages == expected_pages,
              actual_pages)
        route = pages.get("index.html", "")
        try:
            indices = [route.split("<main>", 1)[1].split("<ol>", 1)[1].index(
                'href="' + r.lower() + '.html"') for r in EXPECTED_ROLES]
        except (IndexError, ValueError):
            indices = []
        score(rows, "ROUTE_ORDER", "Core2A→Core1A→Core1B→Core2B",
              len(indices) == 4 and indices == sorted(indices), indices)
        score(rows, "BLUEPRINT_REFERENCE", "zero renderer gaps/advisories/waivers at REFERENCE",
              not (gaps or advisories or waivers),
              {"gaps": gaps, "advisories": advisories, "waivers": waivers})
        for role in EXPECTED_ROLES:
            body = pages.get(role.lower() + ".html", "")
            found = re.findall(r'<article[^>]*data-g9-role="([^"]+)"', body)
            score(rows, "ROLE_" + role, "exact semantic article role in shared renderer",
                  found == [role], {"roles": found, **measure_html(body)})
            crosswalk = golden_role_crosswalk(goldens, role, body)
            score(rows, "GOLDEN_RENDERED_ANATOMY_" + role,
                  "retain nonzero HTML semantic markers shared by both rendered candidate exemplars",
                  crosswalk["passes"], crosswalk,
                  "G-MATH-LINEAR-CONSTRAINT + G-CORE2-R2")
        core1b = pages.get("core1b.html", "")
        score(rows, "T01_T06_T10_T12_RECONSTRUCT", "two distinct attempt gates; boundary and misconception repair",
              len(re.findall(r'<div\b[^>]*data-g9-attempt-box', core1b)) == 2
              and len(re.findall(r'<details\b[^>]*data-requires-attempt', core1b)) == 2
              and "Boundary test" in core1b
              and "Answers that do not yet satisfy the criteria" in core1b,
              measure_html(core1b))
        transfer = pages.get("core2b.html", "")
        visible = Visible()
        visible.feed(transfer)
        score(rows, "T01_T03_TRANSFER_DISCLOSURE", "protected crux inert before learner commitment",
              secret in transfer and secret not in visible.text()
              and 'data-g9-stage="PRE_ATTEMPT"' in transfer
              and 'data-requires-attempt' in transfer,
              {"secret_present_in_html": secret in transfer,
               "secret_visible_precommit": secret in visible.text(),
               **measure_html(transfer)})
        score(rows, "T05_HINTS", "authored opt-in hint access and no precommit answer",
              "Hints after your first attempt" in transfer
              and "data-g9-next-rung" in transfer,
              {"hint_access": "Hints after your first attempt" in transfer,
               "next_rung_control": "data-g9-next-rung" in transfer},
              "G-CORE2-R2")
        score(rows, "T09_CHANGED_DEMAND", "exact selected authored transfer, not another variant",
              transfer_id in transfer
              and all(qid not in transfer for qid in (
                  "Q-TEST-IMO-164-FIVE-CONSECUTIVE-120",
                  "Q-TEST-IMO-164-TRIPLE-12-IFF-BOUNDARY") if qid != transfer_id),
              {"selected_transfer": transfer_id})
        score(rows, "TRACK_B_NON_OVERLAP", "no SOF Core2 source/rights/admission",
              manifest["selection"]["core2"] == []
              and manifest["bank_refs"] == []
              and manifest["coverage"]["sources"] == []
              and "SOF-IMO-G09-" not in " ".join(pages.values()),
              {"core2": manifest["selection"]["core2"], "bank_refs": manifest["bank_refs"]})
        for criterion in ("GOLDEN_VISUAL_GEOMETRY_320_390_768_1280",
                          "HUMAN_AT_KEYBOARD_SCREENREADER_ZOOM",
                          "HUMAN_PHYSICAL_A4",
                          "INDEPENDENT_GRADE9_MATH_QRT",
                          "OWNER_LEARNER_RELEASE"):
            rows.append({"criterion": criterion, "status": "NOT_RUN",
                         "expectation": "dated independent evidence required",
                         "observed": None, "golden_method_reference": None})
        outcomes.append({
            "variant": key, "manifest": str(manifest_path.relative_to(ROOT)),
            "manifest_sha256": digest(manifest_path), "render_digest": render_digest,
            "renderer": render_core.RENDERER_VERSION,
            "selected_transfer": transfer_id,
            "status": "FAIL_TECHNICAL" if any(r["status"] == "FAIL" for r in rows)
                      else "TECHNICAL_HTML_ONLY_PENDING_OTHER_GATES",
            "checks": rows,
        })
    return {
        "schema": "imo-track-a-golden-semantic-benchmark/v1",
        "head": head,
        "pinned_main": BASELINE,
        "renderer_file_digest": digest(ROOT / "Shared/tools/render_core.py"),
        "blueprint_digest": digest(ROOT / "Shared/web/interactive-page-blueprints.v1.json"),
        "goldens": goldens,
        "variants": outcomes,
        "claimed_review": {"golden_owners_blessed": False,
                           "independent_math_accepted": False,
                           "human_accepted": False, "publication": False},
    }


def main(args: list[str]) -> None:
    assert len(args) == 2, "usage: benchmark_imo_173_golden.py <exact-head-sha> <report.json>"
    head, output = args
    assert re.fullmatch(r"[0-9a-f]{40}", head), "must pin exact head"
    report = evaluate(head)
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for candidate in report["variants"]:
        fails = [r["criterion"] for r in candidate["checks"] if r["status"] == "FAIL"]
        print(candidate["variant"], candidate["status"],
              "PASS", sum(r["status"] == "PASS" for r in candidate["checks"]),
              "FAIL", fails, "NOT_RUN",
              sum(r["status"] == "NOT_RUN" for r in candidate["checks"]))
    assert all(c["status"] != "FAIL_TECHNICAL" for c in report["variants"]), "semantic benchmark failed"


if __name__ == "__main__":
    main(sys.argv[1:])
