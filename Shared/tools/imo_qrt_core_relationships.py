#!/usr/bin/env python3
"""Independent source-safe Core1A/Core1B ↔ Core2 relationship evidence audit.

Never treat topic-folder navigation as proof of a concept-specific lesson.
The research builder is not the native render_core.py product.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from Shared.tools import question_review_matrix as qrt
from Shared.tools.imo_qrt_validator import BANKS, BANK_DIR

SCHEMA = "imo-qrt-core-relationship-evidence/v1"
BUILDER = Path("Mathematics/research/build_full_master_suite.py")
UNITS = Path("Mathematics/units")


def _json(path: Path) -> dict[str, Any]:
    d = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(d, dict):
        raise ValueError("INVALID_JSON_OBJECT:" + str(path))
    return d


def topic_map_from_builder(path: Path) -> dict[str, str]:
    """Read literal deployed TOPIC_TO_UNIT_FOLDER from AST, not a guessed duplicate."""
    root = ast.parse(path.read_text(encoding="utf-8"))
    matches = [node.value for node in root.body if isinstance(node, (ast.Assign, ast.AnnAssign))
               and any(isinstance(t, ast.Name) and t.id == "TOPIC_TO_UNIT_FOLDER"
                       for t in (node.targets if isinstance(node, ast.Assign) else [node.target]))]
    if len(matches) != 1:
        raise ValueError("BUILDER_TOPIC_ROUTE_NOT_UNIQUE")
    mapping = ast.literal_eval(matches[0])
    if not isinstance(mapping, dict) or any(not isinstance(k, str) or not isinstance(v, str)
                                            for k, v in mapping.items()):
        raise ValueError("BUILDER_TOPIC_ROUTE_INVALID")
    return mapping


def _pair(core1a_path: Path, units_dir: Path) -> tuple[Path, Path] | None:
    opposite = core1a_path.with_name(core1a_path.name.replace("core1a-", "core1b-", 1))
    if opposite.is_file():
        return core1a_path, opposite
    suffix = ".v1.json" if opposite.name.endswith(".v1.json") else ".json"
    other = opposite.with_name(opposite.name.replace(suffix, ".json" if suffix == ".v1.json" else ".v1.json"))
    return (core1a_path, other) if other.is_file() else None


def audit(*, root: Path = ROOT, baseline_sha: str,
          bank_names: tuple[str, ...] = BANKS) -> dict[str, Any]:
    if len(baseline_sha) != 40 or any(c not in "0123456789abcdef" for c in baseline_sha):
        raise ValueError("EXACT_COMMIT_SHA_REQUIRED")
    bank_dir = root / BANK_DIR.relative_to(ROOT)
    sources = []
    questions: dict[str, dict[str, Any]] = {}
    for name in bank_names:
        f = bank_dir / name
        data = _json(f)
        rows = data.get("questions")
        if not isinstance(rows, list):
            raise ValueError("QUESTIONS_LIST_REQUIRED:" + name)
        sources.append({"path": str(f.relative_to(root)), "sha256": sha256(f.read_bytes()).hexdigest(),
                        "questions": len(rows)})
        for q in rows:
            if not isinstance(q, dict) or not isinstance(q.get("id"), str) or not q["id"]:
                raise ValueError("QUESTION_ID_REQUIRED")
            if q["id"] in questions:
                raise ValueError("DUPLICATE_QUESTION_ID:" + q["id"])
            questions[q["id"]] = q

    units_dir = root / UNITS
    builder = root / BUILDER
    mapping = topic_map_from_builder(builder)
    claims = [
        "Authenticated Core 2 Questions (Click to expand list)",
        "BP-CORE1A &amp; BP-CORE1B CERTIFIED",
    ]
    builder_text = builder.read_text(encoding="utf-8")
    claim_findings = [c for c in claims if c in builder_text]
    all_c1a = sorted(units_dir.glob("*/core1a-*.json"))
    all_c1b = sorted(units_dir.glob("*/core1b-*.json"))
    pairs = []
    explicit = defaultdict(list)
    defects: list[dict[str, str]] = []
    paired_c1b = set()
    for f in all_c1a:
        pair = _pair(f, units_dir)
        if pair is None:
            defects.append({"rule": "CORE1B_PAIR_MISSING", "ref": str(f.relative_to(root))})
            continue
        a_path, b_path = pair
        paired_c1b.add(b_path)
        a, b = _json(a_path), _json(b_path)
        uid = str(a.get("package_id") or a_path.stem)
        refs = a.get("linked_core2_refs", [])
        if not isinstance(refs, list):
            defects.append({"rule": "CORE2_EXPLICIT_LINK_LIST_MALFORMED", "ref": uid})
            refs = []
        for ref in refs:
            if not isinstance(ref, str) or ref not in questions:
                defects.append({"rule": "CORE2_EXPLICIT_REF_NOT_IN_RESEARCH", "ref": str(ref), "unit": uid})
            else:
                explicit[ref].append(uid)
        if len(refs) != len(set(str(x) for x in refs)):
            defects.append({"rule": "CORE2_DUPLICATE_LINK_IN_UNIT", "ref": uid})
        if a.get("topic") and b.get("topic") and a["topic"] != b["topic"]:
            defects.append({"rule": "CORE1A_CORE1B_CONCEPT_ID_MISMATCH", "ref": uid})
        if a.get("subtopic") and not b.get("subtopic"):
            defects.append({"rule": "CORE1B_SUBTOPIC_UNDECLARED", "ref": uid})
        elif a.get("subtopic") and b.get("subtopic") and a["subtopic"] != b["subtopic"]:
            defects.append({"rule": "CORE1A_CORE1B_CONCEPT_ID_MISMATCH", "ref": uid})
        if (a.get("target_band"), a.get("target_demand")) != (b.get("target_band"), b.get("target_demand")):
            defects.append({"rule": "CORE1A_CORE1B_QRT_TARGET_MISMATCH", "ref": uid})
        for role, obj in (("CORE1A", a), ("CORE1B", b)):
            ref = obj.get("blueprint_ref")
            if not isinstance(ref, str) or not ref.startswith("BP-" + role + "-"):
                defects.append({"rule": "RESEARCH_BLUEPRINT_ROLE_NAME_MISMATCH",
                                "ref": uid + ":" + role})
        if a.get("target_demand") not in qrt.DEMANDS or a.get("target_band") not in qrt.BANDS:
            defects.append({"rule": "RESEARCH_UNIT_QRT_LABEL_INVALID", "ref": uid})
        pairs.append({
            "unit_id": uid, "folder": a_path.parent.name,
            "core1a_file": str(a_path.relative_to(root)),
            "core1b_file": str(b_path.relative_to(root)),
            "core1a_sha256": sha256(a_path.read_bytes()).hexdigest(),
            "core1b_sha256": sha256(b_path.read_bytes()).hexdigest(),
            "subtopic": a.get("subtopic"), "target_demand": a.get("target_demand"),
            "target_band": a.get("target_band"), "linked_core2_refs": refs,
            "blueprint_refs": [a.get("blueprint_ref"), b.get("blueprint_ref")],
            "authority": "RESEARCH_ROLE_ASSERTION_ONLY_NOT_NATIVE_BINDING",
        })
    for f in all_c1b:
        if f not in paired_c1b:
            defects.append({"rule": "CORE1B_ORPHAN", "ref": str(f.relative_to(root))})

    folder_unit = defaultdict(list)
    for p in pairs:
        folder_unit[p["folder"]].append(p)
    assignments = []
    proposal_differences = []
    relationship_review_queue = []
    counts = Counter()
    for qid, q in sorted(questions.items()):
        taxonomy = q.get("taxonomy") or {}
        cls = q.get("cognitive_classification") or {}
        raw = str(taxonomy.get("topic_label") or "")
        key = raw.lower().strip()
        declared_folder = mapping.get(key)
        applied_folder = declared_folder or "polynomials"
        routed = folder_unit.get(applied_folder, [])
        linked = explicit.get(qid, [])
        link_kind = "EXPLICIT_UNIT_ID" if linked else (
            "TOPIC_NAV_ONLY" if routed and declared_folder else
            "UNDECLARED_TOPIC_FALLBACK" if not declared_folder else "NO_CORE_UNITS_AT_ROUTED_FOLDER"
        )
        counts[link_kind] += 1
        # Only an explicit declared Core2→Core1A unit ref is structurally
        # stronger than a topic-folder route; neither proves the same crux.
        evidence_kind = {
            "EXPLICIT_UNIT_ID": "DECLARED_CORE1A_LINK_ONLY",
            "TOPIC_NAV_ONLY": "BUILDER_TOPIC_NAVIGATION_ONLY",
            "UNDECLARED_TOPIC_FALLBACK": "BUILDER_DEFAULT_FOLDER_FALLBACK",
            "NO_CORE_UNITS_AT_ROUTED_FOLDER": "NO_ROUTED_CORE_UNIT",
        }[link_kind]
        relationship_code = {
            "EXPLICIT_UNIT_ID": "EXPLICIT_UNIT_INFERENTIAL_JUMP_UNREVIEWED",
            "TOPIC_NAV_ONLY": "TOPIC_ONLY_NOT_CONCEPT_LINK",
            "UNDECLARED_TOPIC_FALLBACK": "UNDECLARED_TOPIC_FALLBACK_NOT_CONCEPT_LINK",
            "NO_CORE_UNITS_AT_ROUTED_FOLDER": "NO_CORE_UNITS_NOT_CONCEPT_LINK",
        }[link_kind]
        relationship_evidence = {
            "rule": "V19", "code": relationship_code,
            "verdict": "REVIEW_REQUIRED",
            "source_basis": evidence_kind,
            "question_id": qid, "topic_label": raw,
            "question_subtopic": taxonomy.get("subtopic"),
            "declared_navigation_folder": declared_folder,
            "navigation_folder_used": applied_folder,
            "explicit_unit_ids": sorted(set(linked)),
            "candidate_unit_ids": [p["unit_id"] for p in routed],
            "same_inferential_jump_proven": False,
            "canonical_core_role_acceptance": "NOT_GRANTED",
        }
        relationship_review_queue.append(relationship_evidence)
        if linked:
            for p in pairs:
                if p["unit_id"] in linked:
                    if p["target_band"] != cls.get("difficulty_band") or p["target_demand"] != cls.get("primary_demand"):
                        counts["EXPLICIT_UNIT_QRT_DIFFERS_FROM_SOURCE_PROPOSAL"] += 1
                        proposal_differences.append({"question_id": qid, "unit_id": p["unit_id"],
                                                     "research_proposed": cls.get("qrt_cell"),
                                                     "unit_target": "QRT-" + str(p["target_demand"]) + "-" + str(p["target_band"]),
                                                     "verdict": "REVIEW_REQUIRED"})
        assignments.append({
            "id": qid, "declared_qrt": cls.get("qrt_cell"),
            "topic_label": raw,
            "builder_navigation_folder": applied_folder,
            "navigation_fallback_used": declared_folder is None,
            "relationship": link_kind,
            "explicit_unit_ids": sorted(set(linked)),
            "candidate_unit_ids": [p["unit_id"] for p in routed],
            "academic_alignment": "REVIEW_REQUIRED",
            "relationship_evidence": relationship_evidence,
            "native_core_admission": "NOT_GRANTED",
        })

    verdict = "FAIL" if defects or counts["UNDECLARED_TOPIC_FALLBACK"] or counts["NO_CORE_UNITS_AT_ROUTED_FOLDER"] else "REVIEW_REQUIRED"
    return {
        "schema": SCHEMA, "source_commit": baseline_sha, "scope": "RESEARCH_RELATIONSHIPS_NOT_PRODUCT_ADMISSION",
        "status": verdict, "source_files": sources, "builder": {
            "path": str(BUILDER), "sha256": sha256(builder.read_bytes()).hexdigest(),
            "unqualified_certification_claims_in_template": claim_findings,
            "default_navigation_folder": "polynomials",
        },
        "question_count": len(questions), "core1a_count": len(all_c1a),
        "core1b_count": len(all_c1b), "paired_units": len(pairs),
        "relationship_counts": dict(sorted(counts.items())), "proposal_differences": proposal_differences,
        "relationship_review_counts": dict(sorted(Counter(
            entry["code"] for entry in relationship_review_queue
        ).items())),
        "relationship_review_queue": relationship_review_queue,
        "structural_findings": defects,
        "academic_approval": "NOT_GRANTED", "source_rights": "NOT_VERIFIED",
        "pairs": pairs, "questions": assignments,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--baseline-sha", required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args(argv)
    result = audit(root=args.root, baseline_sha=args.baseline_sha)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in (
        "schema", "source_commit", "status", "question_count",
        "core1a_count", "core1b_count", "paired_units", "relationship_counts",
        "structural_findings", "proposal_differences", "academic_approval")}, ensure_ascii=False, indent=2))
    return 1 if result["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
