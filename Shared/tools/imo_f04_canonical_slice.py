#!/usr/bin/env python3
"""Real TEST IMO MODEL-D3 QRT + Blueprint + canonical-render audit.

This is an *observer* of existing academic/render authorities, not a QRT,
blueprint, reviewer or release implementation. Generates no public/Docs files.
Only a separately approved reviewer may supply H/S/P/M verdicts.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
from html.parser import HTMLParser
import runpy
import json
from pathlib import Path
import subprocess
import tempfile

from Shared.tools import (
    core_template_contract,
    product_manifest,
    quality_gate,
    question_review_matrix as qrt,
    render_core,
    web_blueprint_contract as blueprints,
)

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "TEST/imo-research/candidates/imo-g9-r1-qrt-core2a-core1a.test.manifest.json"
PACKAGE = ROOT / "TEST/imo-research/candidates/imo-g9-q26-common-base-core1a.v1.json"
PROFILE = ROOT / "Learners/profiles/profile-math-preview.json"
ADAPTER = ROOT / "Mathematics/adapter/DemandReview.json"
F02_SOURCE_CONTRACT = ROOT / "TEST/imo-research/candidates/check_f02_qrt_blueprint_contract.py"
GOLDENS = tuple(ROOT / ("TEST/imo-research/golden/imo-327-" + x + ".v1.json")
                for x in ("explain-d2", "model-d3", "justify-d4"))
QID = "Q-TEST-IMO-G9-COMMON-BASE-SUPPORTED-01"
MID = "MIC-TEST-IMO-G9-COMMON-BASE-RELATION"
STEP = "TC-02"
CELL = "QRT-MODEL-D3"
ROLES = ("CORE1A", "CORE2A")
BLUEPRINT_REFS = {
    "CORE1A": "BP-CORE1A-CONSTRUCTION@1.8.0",
    "CORE2A": "BP-CORE2A-SUPPORTED-APPLICATION@1.1.0",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def held_candidate_findings(manifest: dict, package: dict, *, question_id: str = QID) -> list[str]:
    """Enforce *scope*, not new rights or academic authority."""
    problems = []
    if package.get("subject") != "TEST" or package.get("status") != "CANDIDATE" or manifest.get("subject") != "TEST":
        problems.append("TEST_CANDIDATE_BOUNDARY")
    if manifest.get("output_roles") != list(ROLES):
        problems.append("UNAPPROVED_ROLE_SELECTION")
    if manifest.get("selection", {}).get("core2") or manifest.get("selection", {}).get("core2b"):
        problems.append("SOURCE_OR_TRANSFER_NOT_AUTHORIZED")
    if manifest.get("selection", {}).get("core2a") != [question_id]:
        problems.append("WRONG_CORE2A_QUESTION")
    if manifest.get("selection", {}).get("microtopics") != [MID]:
        problems.append("WRONG_TEACHING_MICROTOPIC")
    if manifest.get("package_refs") != [PACKAGE.relative_to(ROOT).as_posix()]:
        problems.append("MANIFEST_PACKAGE_AUTHORITY_DRIFT")
    extension = package.get("extensions") or {}
    if any(extension.get(flag) is not False for flag in (
        "grade9v3:learner_published",
        "grade9v3:qrt_admitted",
        "grade9v3:core2_source_custody_granted",
    )):
        problems.append("FORGED_PUBLICATION_OR_ACADEMIC_GRANT")
    return problems


def question_by_id(pkg: dict, question_id: str = QID) -> dict:
    matching = [q for q in pkg.get("questions", []) if q.get("id") == question_id]
    if len(matching) != 1 or matching[0].get("origin") != "AUTHORED":
        raise ValueError("expected exactly one authored selected Core2A question")
    return matching[0]


class RenderFacts(HTMLParser):
    """Parse emitted DOM, without altering academic prose or HTML."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root_roles = []
        self.blueprint_refs = []
        self.article_ids = []
        self.templates = []
        self.attempt_details = []
        self.steps = []
        self.repair_links = []
        self.return_links = []
        self.protected = 0
        self._template_depth = 0

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if tag == "html":
            self.root_roles.append(attrs.get("data-g9-role"))
        if tag == "body":
            self.blueprint_refs.append(attrs.get("data-blueprint-ref"))
        if tag == "article":
            self.article_ids.append(attrs.get("id"))
        if tag == "template":
            self._template_depth += 1
            if attrs.get("data-g9-payload"):
                self.templates.append(attrs["data-g9-payload"])
        if tag == "details" and "data-requires-attempt" in attrs:
            self.attempt_details.append(attrs.get("data-g9-payload-ref"))
        if tag == "li" and "data-g9-step" in attrs:
            self.steps.append({"step": attrs.get("data-g9-step"), "id": attrs.get("id")})
        if tag == "a" and "data-g9-repair-ref" in attrs:
            self.repair_links.append({
                "ref": attrs.get("data-g9-repair-ref"),
                "href": attrs.get("href"),
                "protected_template": self._template_depth > 0,
            })
        if tag == "a" and "data-g9-practice-link" in attrs:
            self.return_links.append({
                "question": attrs.get("data-g9-question-ref"),
                "href": attrs.get("href"),
            })

    def handle_endtag(self, tag):
        if tag == "template":
            self._template_depth = max(0, self._template_depth - 1)


def inspect_rendered(pages: dict[str, str], blueprint_refs: dict[str, str]) -> tuple[dict, list[str]]:
    errors = []
    facts = {}
    for role, name in (("CORE1A", "core1a.html"), ("CORE2A", "core2a.html")):
        data = pages.get(name)
        if not isinstance(data, str):
            errors.append(f"MISSING_RENDERED_{role}")
            continue
        parsed = RenderFacts()
        parsed.feed(data)
        parsed.close()
        fact = {
            "root_roles": parsed.root_roles,
            "body_blueprint_refs": parsed.blueprint_refs,
            "article_ids": parsed.article_ids,
            "sha256": sha256(data.encode("utf-8")).hexdigest(),
            "templates": parsed.templates,
            "attempt_detail_refs": parsed.attempt_details,
            "steps": parsed.steps,
            "repair_links": parsed.repair_links,
            "return_links": parsed.return_links,
        }
        facts[role] = fact
        if parsed.root_roles != [role] or parsed.blueprint_refs != [blueprint_refs[role]]:
            errors.append(f"{role}_BLUEPRINT_ROLE_MISMATCH")
        if (MID if role == "CORE1A" else QID) not in parsed.article_ids:
            errors.append(f"{role}_SELECTED_ARTICLE_MISSING")

    core1 = facts.get("CORE1A", {})
    core2 = facts.get("CORE2A", {})
    if not any(s.get("step") == STEP for s in core1.get("steps", [])):
        errors.append("CORE1A_EXACT_STEP_MISSING")
    payload = f"CORE2A-{QID}-reasoning"
    if core2.get("templates", []).count(payload) != 1:
        errors.append("CORE2A_REASONING_TEMPLATE_MISSING")
    if core2.get("attempt_detail_refs", []).count(payload) != 1:
        errors.append("CORE2A_ATTEMPT_GATE_MISSING")
    for link in core2.get("repair_links", []):
        if not link["protected_template"]:
            errors.append("CORE2A_EARLY_REPAIR_LINK")
    return facts, sorted(set(errors))


def navigation_findings(rendered: dict) -> list[str]:
    """Candidate integration gaps, not authority to mutate HTML after rendering."""
    issues = []
    c1 = rendered.get("CORE1A", {})
    c2 = rendered.get("CORE2A", {})
    if sum(s.get("step") == STEP and s.get("id") == STEP for s in c1.get("steps", [])) != 1:
        issues.append("CORE1A_STEP_FRAGMENT_NOT_ADDRESSABLE")
    if sum(l.get("ref") == STEP and l.get("href") == f"core1a.html#{STEP}"
           and l.get("protected_template") for l in c2.get("repair_links", [])) != 1:
        issues.append("CORE2A_NOT_LINKED_TO_EXACT_REPAIR_STEP")
    if sum(l.get("question") == QID and l.get("href") == f"core2a.html#{QID}"
           for l in c1.get("return_links", [])) != 1:
        issues.append("CORE1A_AUTHORED_CORE2A_RETURN_ABSENT")
    return issues


def inspect_real_candidate() -> dict:
    m, package = load(MANIFEST), load(PACKAGE)
    safety = held_candidate_findings(m, package)
    question = question_by_id(package)
    qrt_basis = {"status": "NOT_RUN"}
    f02_source_ledger = {"status": "NOT_RUN"}
    blueprint_basis = {"status": "NOT_RUN"}
    render_basis = {"status": "NOT_RUN"}
    static_gate = {"status": "NOT_RUN"}
    navigation = []
    problems = list(safety)

    # Invoke the canonical 7 x 4 matrix. Never write fabricated reviewer verdicts.
    matrix, vocab = qrt.load(qrt.MATRIX_PATH), qrt.load(qrt.VOCAB_PATH)
    qrt_checks = qrt.check_paths()
    if qrt_checks:
        problems.extend("QRT_MATRIX_" + p for p in qrt_checks)
    resolution = qrt.resolve_review(question, load(PROFILE), matrix, vocab)
    resolution = qrt.specialize_resolution(resolution, load(ADAPTER))
    if resolution["template_id"] != CELL:
        problems.append("QRT_WRONG_RESOLVED_CELL")
    if tuple(resolution["review"]) != qrt.ASKS:
        problems.append("QRT_REVIEW_OBJECTIVES_MISSING")
    qrt_basis = {
        "status": "RESOLVED_AWAITING_INDEPENDENT_SEMANTIC_REVIEW",
        "template_id": resolution["template_id"],
        "classification": resolution["classification"],
        "basis_digests": resolution["basis_digests"],
        "subject_adapter": resolution.get("subject_adapter"),
        "profile": resolution["profile_ref"],
        "profile_fit": "NOT_MEASURED_DESIGN_PREVIEW",
        "slots": resolution["slots"],
        "review_objectives": resolution["review"],  # 12 questions, NO fabricated verdicts
        "reviewer_verdicts": "NOT_PROVIDED",
    }

    registry = blueprints.load_registry()
    # Agent 2's owning F02 semantic-source ledger is the existing authority.
    # Do NOT create a parallel rubric, mark H/S/P/M YES, or reinterpret hints.
    f02_audit = runpy.run_path(str(F02_SOURCE_CONTRACT))["audit"]
    f02_result = f02_audit(package, m, matrix, vocab, registry, [load(g) for g in GOLDENS])
    if f02_result["errors"]:
        problems.extend("F02_SOURCE_CONTRACT_" + p for p in f02_result["errors"])
    if f02_result.get("selected_cell") != resolution["template_id"]:
        problems.append("F02_QRT_CELL_DISAGREEMENT")
    f02_source_ledger = {
        "status": "SOURCE_MAPPED_SEMANTICS_NOT_REVIEWED",
        "selected_cell": f02_result.get("selected_cell"),
        "golden_reference_cells": f02_result.get("golden_reference_cells"),
        "source_hints": f02_result.get("source_hints"),
        "protected_W": f02_result.get("protected_W"),
        "review_gates": f02_result.get("review_gates"),
        "semantic_review_asks": f02_result.get("semantic_review_asks"),
        "required_blueprint_slots": f02_result.get("blueprint_required_slots"),
        "errors": f02_result["errors"],
        "academic_status": f02_result.get("academic_status"),
    }
    audit = blueprints.audit_registry()
    if not audit["passed"]:
        problems.append("BLUEPRINT_REGISTRY_INVALID")
    role_contract = core_template_contract.load_contract()
    refs = {}
    bindings = {}
    for role in ROLES:
        role_row = role_contract["roles"][role]
        ref = role_row["web_blueprint_ref"]
        refs[role] = ref
        issues = blueprints.validate_role_binding(role, role_row, registry)
        if ref != BLUEPRINT_REFS[role] or issues:
            problems.append(f"{role}_BLUEPRINT_BINDING_INVALID")
        bindings[role] = {"ref": ref, "issues": issues}
    blueprint_basis = {"status": "RESOLVED_NOT_PRODUCT_ACCEPTED",
                       "registry_version": registry.get("registry_version"),
                       "registry_audit_passed": audit["passed"],
                       "bindings": bindings}

    with tempfile.TemporaryDirectory(prefix="imo-f04-canonical-test-") as tmp:
        output = Path(tmp) / "render"
        # Canonical renderer writes the real package-selected TEST pages.
        rc = render_core.main(["build", "--manifest", str(MANIFEST),
                               "--out", str(output), "--mode", "PAGES",
                               "--reference", "--draft"])
        if rc != 0:
            problems.append("CANONICAL_RENDER_FAILED")
        elif not (output / "render-receipt.json").is_file():
            problems.append("CANONICAL_RENDER_RECEIPT_MISSING")
        else:
            receipt = load(output / "render-receipt.json")
            pages = {p.name: p.read_text(encoding="utf-8")
                     for p in output.glob("*.html")}
            facts, html_issues = inspect_rendered(pages, refs)
            problems.extend(html_issues)
            navigation = navigation_findings(facts)
            if sorted(pages) != ["core1a.html", "core2a.html", "index.html"]:
                problems.append("UNEXPECTED_RENDERED_ROLES")
            render_basis = {
                "status": "REAL_CANONICAL_TEST_RENDER",
                "receipt": receipt,
                "pages": facts,
                "index_sha256": sha256(pages.get("index.html", "").encode()).hexdigest(),
                "html_contract_findings": html_issues,
                "navigation_findings": navigation,
            }
            # Existing quality gate; static cannot be claimed PASS.
            gate = quality_gate.gate(output, "TEST", m["product_id"], static=True)
            static_gate = {
                "status": "STATIC_ONLY_NOT_BROWSER_ACCEPTANCE",
                "tool": gate["tool"], "verdict": gate["verdict"],
                "rendered_measured": gate["rendered_measured"],
                "fail_reasons": gate["fail_reasons"],
                "finding_count": len(gate["findings"]),
                "findings": gate["findings"],
                "not_measured": gate["not_measured"],
                "continuity": gate["continuity"],
                "pages": gate["pages"],
            }
            if gate["verdict"] == "PASS" or gate["rendered_measured"]:
                problems.append("STATIC_GATE_FALSE_PASS")

    goldens = [{
        "file": p.relative_to(ROOT).as_posix(),
        "sha256": digest(p),
        "declared_status": load(p).get("status"),
        "independent_acceptance": "NOT_GRANTED",
    } for p in GOLDENS]

    return {
        "schema": "agent3-imo-f04-canonical-vertical-slice/v1",
        "state": "BLOCKED" if problems else ("INTEGRATION_GAPS_HELD" if navigation else "EVIDENCE_READY_REVIEW_HOLD"),
        "release_authorized": False,
        "academic_accepted": False,
        "source_core2_eligible": False,
        "owner_merge_authorized": False,
        "profile_personalisation_verified": False,
        "question_id": question["id"],
        "microtopic_id": MID,
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "manifest_sha256": digest(MANIFEST),
        "package_sha256": digest(PACKAGE),
        "qrt": qrt_basis,
        "f02_source_ledger": f02_source_ledger,
        "blueprints": blueprint_basis,
        "render": render_basis,
        "quality_gate": static_gate,
        "goldens": goldens,
        "blocking_findings": sorted(set(problems)),
        "integration_findings": navigation,
        "browser_qa": "NOT_RUN",
        "human_learner_qrt_review": "NOT_RUN",
        "pages_deployment": "NOT_RUN",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write this evidence report to a local build/ file")
    args = parser.parse_args()
    report = inspect_real_candidate()
    text = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        target = args.output.resolve()
        if not target.is_relative_to((ROOT / "build").resolve()) or target == ROOT / "build":
            parser.error("report output must be confined to the local build/ directory")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    print(text)
    return 1 if report["state"] == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
