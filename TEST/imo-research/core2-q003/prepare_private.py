#!/usr/bin/env python3
"""Isolated TEST Core2: private original -> governed render_core, no public source bytes."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STAGE = HERE / ".private"
META = HERE / "custody-receipt.json"

def sha(blob):
    return hashlib.sha256(blob).hexdigest()

def canonical(row):
    return json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()

def validate_private(row, expected, raw):
    for key in ("question_id", "source_url", "pdf_page_index", "printed_page", "printed_question_number"):
        if row.get(key) != expected[key]:
            raise ValueError("SOURCE_IDENTITY_MISMATCH:" + key)
    if sha(raw) != expected["private_input_sha256"]:
        raise ValueError("PRIVATE_INPUT_DIGEST_MISMATCH")
    fields = ("question_id", "stem", "options", "conditions", "figures")
    if not isinstance(row.get("stem"), str) or not row["stem"].strip():
        raise ValueError("STEM_MISSING")
    opts = row.get("options")
    if not isinstance(opts, list) or len(opts) != 4 or any(
        not isinstance(opt, str) or not re.match(r"^[ABCD]\.\s", opt) for opt in opts
    ) or [opt[0] for opt in opts] != list("ABCD"):
        raise ValueError("OPTIONS_MISSING_OR_REORDERED")
    if any(not isinstance(row.get(key), list) for key in ("conditions", "figures", "source_hints")):
        raise ValueError("SOURCE_COMPONENT_MISSING")
    if row["figures"]:
        raise ValueError("FIGURE_ASSET_REQUIRED: no source figure may be silently dropped")
    if sha(canonical({key: row[key] for key in fields})) != expected["source_item_sha256"]:
        raise ValueError("ITEM_COMPONENT_DIGEST_MISMATCH")
    authored = row.get("authored") or {}
    answer = authored.get("answer") or {}
    moves = answer.get("reasoning_route") or []
    if not moves or answer.get("crux_move_ref") not in [m.get("id") for m in moves]:
        raise ValueError("AUTHORED_CRUX_MISSING")
    if not answer.get("summary") or not answer.get("check") or not all(
        m.get("action") and m.get("why_valid") and m.get("output") for m in moves
    ):
        raise ValueError("INCOMPLETE_AUTHORED_REASONING")
    # The Q003 support contract below binds EXACTLY three indexed rungs:
    # neutral pre-attempt orientation, then two protected after-attempt moves.
    # Reject fewer (dangling refs) or more (unguarded/undefined availability).
    if not isinstance(authored.get("scaffolds"), list) or len(authored["scaffolds"]) != 3:
        raise ValueError("QUESTION_SPECIFIC_SUPPORT_REQUIRES_THREE_GATED_RUNGS")

def base_record(name, **fields):
    return dict(id=name, version="0.1.0", status="CANDIDATE",
                source_refs=[], evidence_refs=[], extensions={}, **fields)

def package(expected):
    res = base_record("SRC-IMO-Q003-PRIVATE",
        title="School mirror of original IMO exam paper", origin="WEB",
        locator=expected["source_url"], edition="2023-24", section="Set A Q3",
        last_checked="2026-10-12", access_status="FULL_ITEM_INSPECTED",
        rights_status="NOT_CLEARED_FOR_PUBLICATION",
        snapshot_ref=None, snapshot_digest=None, role=["QUESTION_BANK"],
        supports_claims=[], entry_capabilities=[], depth=["EXAM"],
        selection_reason="Private TEST original-item source", fallback=[])
    bucket = base_record("BUCKET-IMO-NUMERIC-RELATIONSHIPS",
        title="Numerical pair relationships", topic="Logical reasoning",
        intrinsic_badge="MEDIUM", badge_reason="Induce and check a rule across pairs.",
        depth_overlay="EXAM", curriculum_mappings=[], prerequisite_refs=[])
    cap = base_record("CAP-IMO-NUMERIC-RELATIONSHIPS",
        action="Check a candidate numerical relation across all options.",
        success_criterion="Explain a common rule and its unique exception.",
        prerequisite_refs=[], curriculum_mappings=[], external_provider=None,
        acceptance_status="CANDIDATE")
    # A package must contain a microtopic even when only CORE2 is selected.
    # This is an AUTHORED concept candidate, not an original source question
    # or an admitted CORE1A lesson. Do not select/render CORE1A until authored.
    authored = base_record("SRC-IMO-Q003-CONCEPT-AUTHORED",
        title="Authored candidate: checking relations across ordered pairs",
        origin="AUTHORED", locator="TEST/imo-research/core2-q003/prepare_private.py#package",
        edition="2026-10-12", section="TEST concept metadata", last_checked="2026-10-12",
        access_status="FULL_ITEM_INSPECTED", rights_status="AUTHORED_DRAFT_NOT_ACCEPTED",
        snapshot_ref=None, snapshot_digest=None, role=["AUTHOR_CREATED"],
        supports_claims=[], entry_capabilities=[], depth=["EXAM"],
        selection_reason="Separately label test-only concept authoring", fallback=[])
    mic = base_record("MIC-IMO-NUMERIC-RELATIONSHIPS",
        title="Test a consistent rule across numerical pairs",
        bucket_id=bucket["id"], primary_capability_ref=cap["id"],
        intrinsic_badge="MEDIUM",
        badge_reason="One matching pair does not establish a relation for every pair.",
        entry_assumptions=["Can evaluate a numerical expression for a given input."],
        inferential_jump="A proposed input-output rule must explain every pair; one counterexample refutes it.",
        teaching_path=[
            {"id":"IMO-PAIR-M1", "role":"DECLARE",
             "action":"Label each ordered pair as an input and its output.",
             "why_valid":"A relation must map consistently from the same input position.",
             "inputs":[], "output":"Each candidate supplies an input-output check."},
            {"id":"IMO-PAIR-M2", "role":"TRANSFORM",
             "action":"Evaluate one candidate rule for each input and compare its output.",
             "why_valid":"A claimed common rule must hold at every listed pair.",
             "inputs":[], "output":"A match or mismatch is recorded for every pair."},
            {"id":"IMO-PAIR-M3", "role":"VERIFY",
             "action":"Identify whether precisely one pair contradicts the same rule.",
             "why_valid":"A single mismatching pair is an exception only if the others agree.",
             "inputs":[], "output":"An explicitly justified exception or a rejected rule."}
        ],
        relation_refs=[], representation_refs=[], question_family_refs=[],
        misconceptions=[{
            "wrong_idea":"A rule that works for one pair must explain the whole list.",
            "diagnostic_prompt":"What happens when the same rule is applied to a second pair?",
            "repair":"Keep the same operation and check all remaining pairs before selecting an exception."
        }],
        exit_task={
            "prompt":"In an authored list of ordered pairs, one pair matches your proposed rule. Is that enough to establish the rule? Explain your next check.",
            "source_ref":authored["id"],
            "answer":{
                "kind":"MODEL_RESPONSE",
                "summary":"No. Apply the same proposed relation to every ordered pair.",
                "reasoning":[
                    "One matching example does not prove that a rule describes all pairs.",
                    "Evaluate that exact rule on each other input and compare the outputs."
                ],
                "check":"A single genuine mismatch refutes the proposed common rule.",
                "acceptable_alternatives":[], "subpart_answers":[],
                "verification_status":"CHECKED_BY_AUTHOR"
            },
            "oracle":{"no_numeric_claim":"Conceptual rule-consistency decision only; no computed result is asserted."}
        },
        research_contribution="Test-only authored prerequisite for Q003 Core2; not a validated Core1A lesson.",
        prerequisite_refs=[], lineage=[])
    mic["source_refs"] = [authored["id"]]
    # Learner metadata requires a real, package-resolved question family.
    # This is an authored TEST classification, not the original printed label.
    family = base_record("FAM-IMO-NUMERIC-PAIR-RULE-CHECK",
        title="Authored family: numerical pair rule consistency",
        capability_refs=[cap["id"]],
        solution_structure=[
            "Treat each displayed pair as a fixed input-output observation.",
            "Test the same proposed relation on every pair without changing the rule.",
            "Justify the unique mismatch only after verifying the other pairs."
        ],
        demand_dimensions={
            "model_choice":"Select and falsify a common input-output relation.",
            "representation_translation":"Translate the printed ordered pairs into exact input/output checks.",
            "reasoning_steps":"Apply one rule consistently and verify its unique counterexample.",
            "novelty":"A different list of pairs can require a fresh rule, never a memorized option."
        },
        safe_variations=[],
        transfer_boundaries=[
            "Do not assume a rule from only one matching pair.",
            "Do not relabel or reorder the original source options."
        ],
        common_wrong_routes=[
            "Change the candidate rule between options until a chosen answer fits."
        ],
        item_refs=[expected["question_id"]])
    family["source_refs"] = [authored["id"]]
    mic["question_family_refs"] = [family["id"]]
    return dict(schema_version="0.2.0", package_id="TEST-IMO-Q003-CORE2-PRIVATE",
        title="Original numerical pair question / private TEST", version="0.1.0",
        status="CANDIDATE", subject="TEST",
        scope_summary="TEST-only. No QRT, rights, print or publication acceptance.",
        curriculum_mappings=[], resources=[res, authored], buckets=[bucket],
        capabilities=[cap], microtopics=[mic], relations=[], representations=[],
        question_families=[family], questions=[], teaching_routes=[],
        practice_profiles=[], evidence=[], known_issues=[],
        extensions={"grade9v3:publication":"FORBIDDEN"}, data=[])

def bank(row, expected):
    work = row["authored"]
    answer = dict(work["answer"], source_key={"state":"ABSENT"})
    q = dict(id=row["question_id"], version="0.1.0", status="CANDIDATE",
        source_refs=["SRC-IMO-Q003-PRIVATE"], evidence_refs=[],
        origin="LOCAL", origin_ref="SRC-IMO-Q003-PRIVATE",
        original_identifier=row["original_identifier"],
        stem=row["stem"], options=row["options"], conditions=row["conditions"],
        figure_refs=[], subparts=[], hints=row["source_hints"],
        scaffolds=work["scaffolds"], answer=answer,
        response={"type":"single_choice"},
        primary_capability_ref="CAP-IMO-NUMERIC-RELATIONSHIPS",
        secondary_capability_refs=[],
        family_ref="FAM-IMO-NUMERIC-PAIR-RULE-CHECK",
        adaptation=None, exposure=[], extensions={
            # The square-offset model is the learner-owned crux; only neutral
            # option-pair orientation can be shown before commitment.
            # Rungs 1 and 2 materially narrow/complete the protected move.
            "grade9v3:core2_support_plan":{
                "protected_move_refs":[answer["crux_move_ref"]],
                "support_completions":[
                    {"support_ref":"scaffolds[0]",
                     "completed_move_refs":[],
                     "availability":"PRE_ATTEMPT_SAFE"},
                    {"support_ref":"scaffolds[1]",
                     "completed_move_refs":[answer["crux_move_ref"]],
                     "availability":"AFTER_ATTEMPT"},
                    {"support_ref":"scaffolds[2]",
                     "completed_move_refs":[answer["crux_move_ref"]],
                     "availability":"AFTER_ATTEMPT"}
                ]
            },
            # Owner visually verified this exact past-paper item for the private TEST,
            # not its publication rights or publisher-issued source-file digest.
            # Keep that limit explicit; learner metadata refuses an omitted class.
            "grade9v3:provenance_class":"PYQ_VERIFIED",
            "grade9v3:source_custody":{
                "authority_class":"SCHOOL_MIRROR_TEST_REFERENCE",
                "exam":"SOF IMO", "year":"2023-24", "paper":"Set A",
                "question_number":"3", "wording_custody":"VERBATIM_TEST",
                "source_status":"PYQ_VERIFIED_OWNER_INSPECTED_FOR_DEVELOPMENT_ONLY",
                "rights_status":"NOT_GRANTED",
                "paper_url":expected["source_url"],
                "source_item_sha256":expected["source_item_sha256"]},
            "grade9v3:analysis":{
                "topic":"Logical Reasoning",
                "concept_bucket":"BUCKET-IMO-NUMERIC-RELATIONSHIPS",
                "exam_source_badge":"SOF IMO Grade 9 2023-24 Set A Q3 / TEST",
                "original_question_type":"single_correct_mcq",
                "learner_question_type":"single_correct_mcq",
                "difficulty":work["difficulty"],
                "expected_time_seconds":work["expected_time_seconds"],
                "common_wrong_route":work.get("common_wrong_route",
                    "Guessing without checking one rule consistently."),
                "stable_crux_move":answer["crux_move_ref"],
                "transfer_profile":{"core2b_candidate":False,
                    "dimension":None, "classification":"SOURCE_TEST_ONLY"}},
            "grade9v3:component_waivers":{
                "REPRESENTATION":"This original item has pairs, not a source drawing.",
                "CONDITIONS":"No separately printed item conditions."}})
    return {"schema_version":"imo-private-test-bank-v1", "questions":[q]}

def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")

def prepare(private_path, custody_receipt=META):
    # A reconstituted local input must name its own SHA-pinned receipt explicitly.
    # The default remains the frozen predecessor custody receipt, unchanged.
    expected = json.loads(custody_receipt.read_text(encoding="utf-8"))
    raw = private_path.read_bytes()
    row = json.loads(raw.decode("utf-8"))
    validate_private(row, expected, raw)
    STAGE.mkdir(parents=True, exist_ok=True)
    write_json(STAGE / "records.json", package(expected))
    write_json(STAGE / "bank.json", bank(row, expected))
    rel = lambda p: p.relative_to(ROOT).as_posix()
    write_json(STAGE / "manifest.json", dict(
        schema="product-manifest/v1", product_id="TEST-IMO-Q003-CORE2",
        subject="TEST", home_href="index.html", question_bank_href="index.html",
        package_refs=[rel(STAGE / "records.json")],
        bank_refs=[rel(STAGE / "bank.json")],
        selection={"microtopics":[], "core2":[expected["question_id"]],
                   "core2a":[], "core2b":[]}, output_roles=["CORE2"]))
    return expected, row

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--private-input", required=True, type=Path)
    ap.add_argument("--custody-receipt", type=Path, default=META,
                    help="Explicit local SHA-pinned custody receipt; default is committed frozen receipt")
    ap.add_argument("--prepare-only", action="store_true")
    args = ap.parse_args()
    if not args.private_input.is_file():
        ap.error("private input is required, never committed")
    if not args.custody_receipt.is_file():
        ap.error("custody receipt is required for this input; it may be kept locally")
    expected, row = prepare(args.private_input, args.custody_receipt)
    if args.prepare_only:
        print("PRIVATE_TEST_FIXTURE_PREPARED; renderer not executed")
        return 0
    sys.path.insert(0, str(ROOT))
    from Shared.tools import render_core
    render_dir = STAGE / "rendered"
    result = render_core.main(["build", "--manifest", str(STAGE / "manifest.json"),
        "--out", str(render_dir), "--mode", "PAGES", "--draft", "--reference"])
    if result:
        return result
    html = (render_dir / "core2.html").read_text(encoding="utf-8")
    if row["stem"] not in html or not all(option in html for option in row["options"]):
        raise ValueError("RENDER_STEM_OR_ORDERED_OPTIONS_MISSING")
    if 'data-g9-commit' not in html or 'data-g9-response-type="single_choice"' not in html:
        raise ValueError("RENDER_COMMIT_MISSING")
    receipt = json.loads((render_dir / "render-receipt.json").read_text(encoding="utf-8"))
    write_json(STAGE / "sanitized-render-receipt.json", {
        "issue":183, "task":"183-T2", "question_id":expected["question_id"],
        "source_item_sha256":expected["source_item_sha256"],
        "private_input_sha256":expected["private_input_sha256"],
        "rendered_core2_sha256":sha((render_dir / "core2.html").read_bytes()),
        "renderer_digest":receipt["digest"], "renderer_gap_count":len(receipt["gaps"]),
        "role":"CORE2", "mode":"PAGES", "draft":True,
        "owner_qrt_accepted":False, "publisher_rights_granted":False,
        "same_page_a4_receipt":"NOT_RUN", "published":False})
    print("PRIVATE_TEST_RENDER_DONE: source bytes and learner HTML excluded from Git")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
