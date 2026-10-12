#!/usr/bin/env python3
"""SHA-gated private Q003 -> authored Core1A records -> sole registered renderer.

No original question words, options, private JSON, or output HTML are committed.
The source-safe authored inputs are in core1a-authored.v1.json.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STAGE = HERE / ".private" / "core1a"
AUTHOR = HERE / "core1a-authored.v1.json"
META = HERE / "custody-receipt.json"
sys.path.insert(0, str(HERE))
import prepare_private as core2_adapter  # existing exact original + source-component SHA guard


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _author_transfer(authored: dict, source_ref: str, capability_ref: str, family_ref: str) -> dict:
    t = authored["authored_transfer"]
    pairs = t["pairs"]
    residuals = [y - x * x for x, y in pairs]
    if residuals != t["expected_residuals"] or len(pairs) != 4:
        raise ValueError("AUTHORED_TRANSFER_MATH_MISMATCH")
    offset = t["common_offset"]
    exception = t["exception_zero_based"]
    if sum(r == offset for r in residuals) != 3 or residuals[exception] == offset:
        raise ValueError("AUTHORED_TRANSFER_EXCEPTION_MISMATCH")
    return {
        "id": t["id"], "version": "0.1.0", "status": "CANDIDATE",
        "source_refs": [source_ref], "evidence_refs": [], "extensions": {},
        "origin": "AUTHORED", "origin_ref": source_ref,
        "original_identifier": "AUTHOR-IMO-PAIR-TRANSFER-2026-10-12",
        "stem": t["stem"], "subparts": [], "options": [], "conditions": [],
        "figure_refs": [], "response": {"type": "short_text"},
        "answer": {
            "kind": "MODEL_RESPONSE", "summary": t["answer_summary"],
            "reasoning": t["reasoning"], "check": t["independent_check"],
            "acceptable_alternatives": [], "subpart_answers": [],
            "verification_status": "CHECKED_BY_AUTHOR",
        },
        "primary_capability_ref": capability_ref, "secondary_capability_refs": [],
        "family_ref": family_ref, "adaptation": None,
        "exposure": [{"core": "CORE1A", "role": "PLANNED_WORKED_ANCHOR", "artifact_ref": None}],
    }


def stage_private(original: Path, receipt: Path) -> dict:
    expected = json.loads(receipt.read_text(encoding="utf-8"))
    raw = original.read_bytes()
    source = json.loads(raw.decode("utf-8"))
    core2_adapter.validate_private(source, expected, raw)
    authored = json.loads(AUTHOR.read_text(encoding="utf-8"))
    if (authored.get("schema") != "q003-core1a-authored-input/v1"
            or authored.get("question_ref") != expected["question_id"]
            or authored.get("origin") != "AUTHORED"):
        raise ValueError("CORE1A_AUTHORED_SCOPE_OR_ORIGINAL_ID_INVALID")
    result = core2_adapter.package(expected)
    mic = next(m for m in result["microtopics"] if m["id"] == authored["microtopic_id"])
    for key in ("title", "inferential_jump", "entry_assumptions",
                "teaching_path", "misconceptions", "construction_units", "exit_task"):
        mic[key] = authored[key]
    # Native registered relation and authored staged representation; never
    # source components, placeholder HTML, or copies of private source options.
    for collection in ("relations", "representations"):
        rows = authored.get(collection) or []
        if not isinstance(rows, list) or not rows:
            raise ValueError("CORE1A_AUTHORED_" + collection.upper() + "_MISSING")
        existing = {record["id"] for record in result[collection]}
        for record in rows:
            if record["id"] in existing or record.get("source_refs") != ["SRC-IMO-Q003-CONCEPT-AUTHORED"]:
                raise ValueError("CORE1A_AUTHORED_" + collection.upper() + "_IDENTITY_INVALID")
            result[collection].append(record)
            existing.add(record["id"])
    mic["relation_refs"] = [r["id"] for r in authored["relations"]]
    mic["representation_refs"] = [r["id"] for r in authored["representations"]]
    if len(mic["construction_units"]) < 1:
        raise ValueError("CORE1A_CONSTRUCTION_UNITS_MISSING")
    ids = {step["id"] for step in mic["teaching_path"]}
    for unit in mic["construction_units"]:
        if not set(unit["step_refs"]) <= ids:
            raise ValueError("CORE1A_UNIT_STEP_REF_MISSING")
        if unit.get("crux_question_refs") and unit["crux_question_refs"] != [expected["question_id"]]:
            raise ValueError("CORE1A_ORIGINAL_QUESTION_REF_MISMATCH")
    # This is a wholly authored worked anchor, not a relabelled original.
    authored_worked = _author_transfer(
        authored, "SRC-IMO-Q003-CONCEPT-AUTHORED",
        mic["primary_capability_ref"], mic["question_family_refs"][0],
    )
    result["questions"].append(authored_worked)
    bank = core2_adapter.bank(source, expected)  # private original, no re-keying

    # The native Core1A toughest-concept contract requires a separate worked
    # teaching anchor bound to the actual source question's exact crux move.
    # That private crux ref is read from the SHA-validated bank, never guessed,
    # transcribed into authored Git data, or replaced by a generic topic label.
    original = next(q for q in bank["questions"] if q["id"] == expected["question_id"])
    crux = original["answer"]["crux_move_ref"]
    moves = {move["id"] for move in original["answer"]["reasoning_route"]}
    if crux not in moves:
        raise ValueError("CORE1A_AUTHENTIC_CRUX_UNRESOLVED")
    anchors = {}
    for binding in authored.get("lesson_anchor_bindings") or []:
        unit = next((u for u in mic["construction_units"]
                     if u["id"] == binding.get("construction_ref")), None)
        if (unit is None or unit["id"] in anchors
                or binding.get("target_question_ref") != original["id"]
                or binding.get("authored_worked_ref") != authored_worked["id"]
                or binding.get("target_crux_move_ref_source") != "SHA_VALIDATED_PRIVATE_BANK"
                or original["id"] not in (unit.get("crux_question_refs") or [])
                or unit.get("crux_step_ref") not in (unit.get("step_refs") or [])):
            raise ValueError("CORE1A_LESSON_ANCHOR_SCOPE_INVALID")
        anchor = {
            "id": binding["id"],
            "construction_ref": unit["id"],
            "target_question_ref": original["id"],
            "target_crux_move_ref": crux,
            "stem": authored_worked["stem"],
            "answer": authored_worked["answer"],
        }
        sys.path.insert(0, str(ROOT))
        from Shared.tools import learning_repair  # native anchor binding validator
        problems = learning_repair.anchor_problems(
            anchor, {original["id"]: original}, unit["id"],
            expected_ref=original["id"])
        if problems:
            raise ValueError("CORE1A_LESSON_ANCHOR_INVALID: " + "; ".join(problems))
        anchors[unit["id"]] = anchor
    if not anchors:
        raise ValueError("CORE1A_TARGET_CRUX_LESSON_ANCHOR_MISSING")
    mic["extensions"]["grade9v3:lesson_anchors"] = anchors
    write_json(STAGE / "records.json", result)
    write_json(STAGE / "bank.json", bank)
    rel = lambda p: p.relative_to(ROOT).as_posix()
    write_json(STAGE / "manifest.json", {
        "schema": "product-manifest/v1", "product_id": "TEST-IMO-Q003-CORE1A",
        "subject": "TEST", "home_href": "index.html",
        "question_bank_href": "index.html",
        "package_refs": [rel(STAGE / "records.json")],
        "bank_refs": [rel(STAGE / "bank.json")],
        "selection": {
            "microtopics": [mic["id"]],
            "core2": [expected["question_id"]],
            "core2a": [], "core2b": []
        },
        "output_roles": ["CORE1A"]
    })
    print("CORE1A_PRIVATE_FIXTURE_PREPARED; original input verified and retained locally only")
    return expected


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--private-input", type=Path, required=True)
    ap.add_argument("--custody-receipt", type=Path, default=META)
    ap.add_argument("--prepare-only", action="store_true")
    args = ap.parse_args()
    if not args.private_input.is_file() or not args.custody_receipt.is_file():
        ap.error("BLOCKED: secure original and its SHA-pinned custody receipt required")
    if not (ROOT / "Shared/tools/render_core.py").is_file():
        ap.error("BLOCKED: full native Shared/tools/render_core.py checkout required")
    expected = stage_private(args.private_input, args.custody_receipt)
    if args.prepare_only:
        return 0
    sys.path.insert(0, str(ROOT))
    from Shared.tools import render_core  # sole registered page renderer
    output = STAGE / "rendered"
    ret = render_core.main([
        "build", "--manifest", str(STAGE / "manifest.json"),
        "--out", str(output), "--mode", "PAGES", "--draft", "--reference"
    ])
    if ret:
        return ret
    page = output / "core1a.html"
    if not page.is_file():
        raise ValueError("NATIVE_CORE1A_PAGE_MISSING")
    html = page.read_text(encoding="utf-8")
    if "BP-CORE1A-CONSTRUCTION" not in html or 'data-g9-role="CORE1A"' not in html:
        raise ValueError("CORE1A_REGISTERED_BLUEPRINT_OR_ROLE_MISSING")
    if "AUTHORED TRANSFER" not in html or "AUTHORED INDEPENDENT EXIT" not in html:
        raise ValueError("CORE1A_AUTHORED_ANCHOR_OR_EXIT_MISSING")
    receipt = json.loads((output / "render-receipt.json").read_text(encoding="utf-8"))
    write_json(STAGE / "source-safe-core1a-receipt.json", {
        "issue": 183, "task": "183-T4-G2-W1", "aim": "v3.1.0",
        "original_question_id": expected["question_id"],
        "original_input_sha256": expected["private_input_sha256"],
        "original_item_sha256": expected["source_item_sha256"],
        "author_input_sha256": sha256(AUTHOR.read_bytes()).hexdigest(),
        "core1a_page_sha256": sha256(page.read_bytes()).hexdigest(),
        "core1a_page_bytes": page.stat().st_size,
        "renderer": receipt.get("renderer"), "renderer_digest": receipt.get("digest"),
        "renderer_gaps": len(receipt.get("gaps", [])),
        "registered_blueprint": "BP-CORE1A-CONSTRUCTION",
        "same_page_a4": "NOT_RUN", "owner_qrt_accepted": False,
        "publisher_rights_granted": False, "published": False,
    })
    print("CORE1A_NATIVE_RENDER_DONE; original and learner HTML remain private")
    print("source-safe receipt: " + str(STAGE / "source-safe-core1a-receipt.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
