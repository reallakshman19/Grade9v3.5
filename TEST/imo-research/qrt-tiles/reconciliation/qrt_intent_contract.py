#!/usr/bin/env python3
"""Issue #182 R8 P0: provenance-bound QRT Intent Contract for authored TEST cells.

This is a TEST verifier, NOT a QRT classifier, learner-performance assessor,
blueprint authority, golden rewrite, or academic/Owner acceptance mechanism.
Use against an exact source checkout. Intent declarations are review hypotheses.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re

DEMANDS = ("RETRIEVE", "EXPLAIN", "APPLY", "MODEL",
           "REPRESENT", "SYNTHESIZE", "JUSTIFY")
BANDS = ("D1", "D2", "D3", "D4")
ROLES = ("CORE1", "CORE1A", "CORE1B", "CORE2A", "CORE2B")
REVIEWS = tuple(f"{family}{i}" for family in "HSPM" for i in (1, 2, 3))
BP = {
    "CORE1": "BP-CORE1-ORIENTATION@1.1.0",
    "CORE1A": "BP-CORE1A-CONSTRUCTION@1.8.0",
    "CORE1B": "BP-CORE1B-RECONSTRUCTION@1.1.0",
    "CORE2A": "BP-CORE2A-SUPPORTED-APPLICATION@1.1.0",
    "CORE2B": "BP-CORE2B-TRANSFER@1.1.0",
}
TECHNIQUES = {
    "CORE1": ["T14"],
    "CORE1A": ["T02", "T03", "T11"],
    "CORE1B": ["T06", "T10", "T12"],
    "CORE2A": ["T05", "T07"],
    "CORE2B": ["T08", "T09"],
}
CANONICAL_BLOBS = {
    "matrix": "3779a53ae7d20efbb4644bc3f9243909e93dc145",
    "templates": "e2409aef11ae7d98444593bfbe1a38eb00c97cef",
    "registry": "591ba061b8771c30fdffc4506aa720ca9ba89335",
}
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class ContractError(ValueError):
    """Stable fail-closed error identifier; never an academic determination."""


def ensure(condition: bool, code: str, detail: str = "") -> None:
    if not condition:
        raise ContractError(f"{code}: {detail}")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def blob_hash(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(payload)).encode("ascii") +
                        b"\\0" + payload).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_under(root: Path, path: str) -> Path:
    root = root.resolve()
    candidate = (root / path).resolve()
    ensure(candidate.is_relative_to(root), "PATH_ESCAPE", path)
    ensure(candidate.is_file(), "SOURCE_MISSING", path)
    return candidate


def canonical(authority_root: Path) -> tuple[dict, dict, dict]:
    paths = {
        "matrix": "Shared/quality/question-demand-matrix.v1.json",
        "templates": "Shared/quality/question-demand-templates.v1.json",
        "registry": "Shared/web/interactive-page-blueprints.v1.json",
    }
    objects = {}
    for label, relative in paths.items():
        path = resolve_under(authority_root, relative)
        ensure(blob_hash(path) == CANONICAL_BLOBS[label],
               "CANONICAL_DRIFT", f"{label} does not match locked blob")
        objects[label] = read_json(path)
    matrix, templates, registry = (
        objects["matrix"], objects["templates"], objects["registry"]
    )
    expected = {f"QRT-{d}-{b}" for d in DEMANDS for b in BANDS}
    ids = [t["template_id"] for t in templates["templates"]]
    ensure(len(ids) == 28 and len(set(ids)) == 28 and set(ids) == expected,
           "CANONICAL_28_CELLS", str(len(ids)))
    ensure(set(matrix["demands"]) == set(DEMANDS) and
           set(matrix["band_policies"]) == set(BANDS),
           "CANONICAL_VOCAB_DRIFT")
    indexed = {f"{item['id']}@{item['version']}" for item in registry["blueprints"]}
    ensure(set(BP.values()).issubset(indexed),
           "BLUEPRINT_DRIFT", "five pinned role blueprints missing")
    return matrix, templates, registry


def validate_payload(source: dict, manifest: dict, matrix: dict,
                     template: dict, witness: dict) -> dict:
    """Contract validation: provenance/links and declared review claims only."""
    cell = witness.get("cell_id")
    ensure(isinstance(cell, str) and re.fullmatch(r"QRT-[A-Z]+-D[1-4]", cell),
           "CELL_ID", str(cell))
    _, demand, band = cell.split("-")
    ensure(demand in DEMANDS and band in BANDS, "UNKNOWN_DEMAND_BAND")
    ensure(template["template_id"] == cell and
           template["demand"] == demand and template["band"] == band,
           "TEMPLATE_CELL_DRIFT")
    ensure(template["decisive_act"] == matrix["demands"][demand]["decisive_act"],
           "CANONICAL_ACT_DRIFT")
    ensure(template["band_policy"] == matrix["band_policies"][band],
           "CANONICAL_BAND_DRIFT")
    ensure(set(template["slots"]) == {
        "X", "Y", "Z", "W", "wrong_idea", "replacement_rule",
        "visual_job", "check_job"}, "CANONICAL_SLOTS_DRIFT")
    ensure(set(template["review"]) == set(REVIEWS),
           "TWELVE_SEMANTIC_OBJECTIVES")
    ensure(all(template["review"][k].get("question") and
               template["review"][k].get("objective") for k in REVIEWS),
           "REVIEW_OBJECTIVE_EMPTY")

    rival = witness.get("strongest_rival")
    ensure(rival in DEMANDS and rival != demand, "RIVAL_REQUIRED")
    ensure(len(str(witness.get("success_evidence", "")).strip()) >= 45,
           "SUCCESS_EVIDENCE_REQUIRED")
    ensure(len(str(witness.get("question_specific_W", "")).strip()) >= 35,
           "QUESTION_SPECIFIC_W_REQUIRED")
    falsifier = witness.get("falsifier")
    ensure(isinstance(falsifier, dict) and
           len(str(falsifier.get("hypothesis", "")).strip()) >= 30 and
           falsifier.get("probe_kind") in
           ("SOURCE_STEM_METHOD_CUE", "REVIEW_HYPOTHESIS"),
           "FALSIFIER_REQUIRED")

    ensure(manifest.get("output_roles") == list(ROLES) and
           manifest.get("selection", {}).get("core2") == [],
           "FIVE_TEST_ROLES_ONLY")
    ensure(source.get("subject") == "TEST" and
           source.get("status") == "CANDIDATE",
           "AUTHOR_TEST_SCOPE")
    qmap = {q["id"]: q for q in source.get("questions", [])}
    ensure(len(qmap) == len(source.get("questions", [])),
           "DUPLICATE_QUESTION_IDS")
    sel = manifest.get("selection", {})
    ensure(len(sel.get("core2a", [])) == 1 and
           len(sel.get("core2b", [])) == 1, "QUESTION_SELECTION")
    ensure(witness.get("primary_question_id") == sel["core2a"][0] and
           witness.get("transfer_question_id") == sel["core2b"][0],
           "WITNESS_SELECTION_DRIFT")
    ensure(sel["core2a"][0] in qmap and sel["core2b"][0] in qmap,
           "SELECTED_QUESTION_NOT_FOUND")
    ensure(sel["core2a"][0] != sel["core2b"][0],
           "TRANSFER_NOT_NEW_QUESTION")
    ensure(len(sel.get("microtopics", [])) >= 1 and
           set(sel["microtopics"]).issubset({m["id"] for m in source.get("microtopics", [])}),
           "MISSING_MICROTOPIC")
    outputs = {}
    for role, qid in (("primary", sel["core2a"][0]),
                      ("transfer", sel["core2b"][0])):
        q = qmap[qid]
        cognitive = q.get("extensions", {}).get("grade9v3:cognitive_demand", {})
        ensure(cognitive.get("primary") == demand,
               "QUESTION_DEMAND_DRIFT", f"{role} {qid}")
        difficulty = q.get("difficulty", {})
        ensure(difficulty.get("band") == band,
               "QUESTION_BAND_DRIFT", f"{role} {qid}")
        route = q.get("answer", {}).get("reasoning_route", [])
        crux = q.get("answer", {}).get("crux_move_ref")
        matches = [move for move in route if move.get("id") == crux]
        ensure(isinstance(crux, str) and len(matches) == 1,
               "UNRESOLVED_CRUX", f"{role} {qid}")
        ensure(witness.get(f"{role}_crux_move_ref") == crux,
               "WITNESS_CRUX_DRIFT", f"{role} {qid}")
        if role == "primary":
            ensure(rival in cognitive.get("secondary", []),
                   "RIVAL_NOT_GROUNDED_IN_SOURCE", rival)
        components = difficulty.get("components", {})
        ensure(len(components) == 5 and
               all(isinstance(v, int) and 0 <= v <= 2
                   for v in components.values()) and
               difficulty.get("score") == sum(components.values()),
               "DIFFICULTY_COMPONENTS_DRIFT", qid)
        ensure(str(q.get("stem", "")).strip(),
               "MISSING_STEM", qid)
        outputs[role] = {
            "question_id": qid,
            "crux_move_ref": crux,
            "crux_kind": matches[0].get("kind"),
            "crux_action": matches[0].get("action"),
            "difficulty_score": difficulty["score"],
            "declared_demand": demand,
            "declared_band": band,
        }

    ensure(outputs["primary"]["crux_move_ref"] !=
           outputs["transfer"]["crux_move_ref"],
           "TRANSFER_REUSED_PRIMARY_CRUX")

    observed = False
    if falsifier["probe_kind"] == "SOURCE_STEM_METHOD_CUE":
        ensure(cell == "QRT-RETRIEVE-D2",
               "UNSUPPORTED_CUE_PROBE")
        stem = qmap[sel["core2a"][0]]["stem"]
        observed = bool(re.search(
            r"\\bretrieve\\b.{0,50}\\bright.triangle distance relation\\b",
            stem, flags=re.I
        ))
        ensure(observed, "METHOD_CUE_EXPECTATION_DRIFT",
               "the known held RETRIEVE-D2 method cue disappeared")
    return {
        "cell_id": cell, "primary_demand": demand,
        "strongest_rival": rival, "band": band,
        "canonical_decisive_act": template["decisive_act"],
        "canonical_X_Y_Z_W": copy.deepcopy(template["slots"]),
        "canonical_band_policy": copy.deepcopy(template["band_policy"]),
        "question_specific_W": witness["question_specific_W"],
        "success_evidence_hypothesis": witness["success_evidence"],
        "falsifier": {**falsifier, "specific_source_cue_observed": observed},
        "source_crux": outputs, "learner_prior_knowledge_status":
            witness.get("Y_evidence_status", "UNKNOWN"),
        "semantic_objectives": {
            key: {"objective": template["review"][key]["objective"],
                  "question": template["review"][key]["question"],
                  "verdict": "NOT_RUN", "evidence": []}
            for key in REVIEWS
        },
        "roles": {
            role: {"blueprint": BP[role], "golden_techniques": TECHNIQUES[role],
                   "engineering": "NOT_RUN", "semantic": "NOT_RUN",
                   "evidence": [], "role_W_assessment": "NOT_RUN"}
            for role in ROLES
        },
        "whole_journey_W": {"status": "NOT_RUN",
                            "paths_checked": [],
                            "assisted_retry_is_independent": False},
        "technical_contract": "VALIDATED_PROPOSAL",
        "semantic_review": "HOLD_REVIEW_REQUIRED",
        "qualified_academic_review": "PENDING",
        "owner_qrt_acceptance": "PENDING",
        "publication": "FORBIDDEN",
        "note": ("Source metadata and supplied review assertions are confirmed "
                 "for provenance/consistency, NOT for academic truth. "
                 "Specific falsifiers can prove a defect, but absence of "
                 "detected cues cannot establish cognitive independence."),
    }


def compile_contract(authority_root: Path, source_root: Path,
                     witness_path: Path, ledger_path: Path) -> dict:
    matrix, templates, _ = canonical(authority_root)
    witness = read_json(witness_path)
    rows = read_json(ledger_path).get("rows", [])
    cell = witness.get("cell_id")
    row = next((x for x in rows if x.get("cell_id") == cell), None)
    ensure(row is not None, "LEDGER_CELL_MISSING", str(cell))
    expected = witness.get("source_pin", {})
    ensure(expected.get("commit") and
           expected["commit"] in (row["source"]["commit"], witness.get("source_alternate_commit")),
           "SOURCE_PIN_REQUIRED", str(cell))
    for label in ("source", "manifest"):
        ensure(expected.get(f"{label}_path") == row[label]["path"],
               "LEDGER_PATH_DRIFT", label)
        ensure(expected.get(f"{label}_blob") == row[label]["git_blob_sha"],
               "LEDGER_BLOB_DRIFT", label)
    paths = {key: resolve_under(source_root, expected[f"{key}_path"])
             for key in ("source", "manifest")}
    for key, path in paths.items():
        ensure(blob_hash(path) == expected[f"{key}_blob"],
               "SOURCE_BYTES_DRIFT", f"{key}: {path}")
    manifest = read_json(paths["manifest"])
    ensure(manifest.get("package_refs") == [expected["source_path"]],
           "MANIFEST_SOURCE_BINDING_DRIFT")
    source = read_json(paths["source"])
    template = next((x for x in templates["templates"] if x["template_id"] == cell), None)
    ensure(template is not None, "CELL_TEMPLATE_MISSING")
    contract = validate_payload(source, manifest, matrix, template, witness)
    contract["provenance"] = {
        "declared_source_commit": expected["commit"],
        "source_path": expected["source_path"],
        "source_git_blob": blob_hash(paths["source"]),
        "source_sha256": sha256(paths["source"]),
        "manifest_path": expected["manifest_path"],
        "manifest_git_blob": blob_hash(paths["manifest"]),
        "manifest_sha256": sha256(paths["manifest"]),
        "matrix_git_blob": CANONICAL_BLOBS["matrix"],
        "templates_git_blob": CANONICAL_BLOBS["templates"],
        "registry_git_blob": CANONICAL_BLOBS["registry"],
        "adoption_ledger_sha256": sha256(ledger_path),
        "witness_sha256": sha256(witness_path),
        "golden_reference": "G-IMO-G9-FIVE-CORE-20261012",
        "golden_verification": "NOT_RUN",
    }
    return contract


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authority-root", type=Path, default=Path("."))
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--witness-file", type=Path, required=True)
    parser.add_argument("--adoption-ledger", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    contract = compile_contract(args.authority_root, args.source_root,
                                args.witness_file, args.adoption_ledger)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\\n",
                        encoding="utf-8")
    print(f"{contract['cell_id']}: provenance+QRT Intent Contract VALIDATED_PROPOSAL; "
          f"academic/Owner HOLD; five Core semantic roles NOT_RUN")
    if contract["falsifier"]["specific_source_cue_observed"]:
        print("Existing learner method-cue falsifier OBSERVED; "
              "primary-vs-rival classification remains reviewer HOLD")


if __name__ == "__main__":
    main()
