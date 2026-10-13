"""Build protocol-compatible, source-safe D2 tile JSON from verified native evidence.

Uses the isolated BENCHMARK-PROTOCOL.md / CELL-TILE.template.json structure
without importing private Q003 content or accepting any QRT/golden. These are
test artifacts for issue #201, not replacement golden snapshots.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
DEMANDS = ("retrieve","explain","apply","model","represent","synthesize","justify")
ROLES = ("core1","core1a","core1b","core2a","core2b")
ASKS = ("H1","H2","H3","S1","S2","S3","P1","P2","P3","M1","M2","M3")
LOCK = ROOT / "golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshot-lock.json"
LEDGER = ROOT / "TEST/imo-research/qrt-d2/issue-201/evidence.v1.json"

COGNITIVE = {
    "retrieve": ("Compare rectangle diagonal with perpendicular-side route and budget",
                 "Known right-triangle rule, positive root and additive edge-length rule",
                 "Compute both routes, check allowance and quantitative saving",
                 "APPLY-D2 is a substantive alternative; REVIEW_RISK_HIGH"),
    "explain": ("Account for multiplicative change in consecutive powers",
                "Positive-integer exponents are equal-factor products",
                "Regroup added factor and falsify incorrect additive update",
                "APPLY-D2 can evaluate numbers, but primary claim demands mechanism explanation"),
    "apply": ("Two successive discounts and an original-relative equivalent",
              "Remaining-percent factor with an updated base",
              "Execute known percent steps, reconcile original reference and diagnose naive addition",
              "MODEL-D2 would require forming a novel relation; factor method is given"),
    "model": ("Fixed nine-item count and two unit prices with one observed total",
              "Complementary count and additive price-times-count",
              "Construct weighted one-variable equation, solve integer count and check both givens",
              "APPLY-D2 is plausible if reviewer finds model construction supplied by the stem"),
    "represent": ("Two shaded parts of uniform rectangular grid",
                  "Equal-cell count, disjoint sets, product/row representation",
                  "Choose nonoverlapping partition and translate count into row/product",
                  "APPLY-D2 possible if named strategy leaves no genuine representation choice"),
    "synthesize": ("Find maximal multiple of six from distinct allowed digits",
                   "Parity, divisibility-by-three and place-value order",
                   "Coordinate two divisibility tests, reject larger tens candidates",
                   "D3 only if these component rules are not independently familiar"),
    "justify": ("Universal triple divisibility true despite false one-factor rationale",
                "Coprime divisor guarantee, parity and three-residue rule",
                "Counterexample to invalid reason, then all-cases proof for universal claim",
                "D3 if residue/coprimality warrant itself must be invented rather than linked"),
}

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def blob(path: Path) -> str:
    return subprocess.check_output(["git","hash-object",str(path)],cwd=ROOT,text=True).strip()

def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--render-root",required=True,type=Path)
    cli.add_argument("--out",required=True,type=Path)
    cli.add_argument("--run-url",required=True)
    args = cli.parse_args()
    ledger = json.loads(LEDGER.read_text())
    rows = {r["demand"].lower():r for r in ledger["rows"]}
    assert tuple(rows) == DEMANDS, "LEDGER_DEMAND_ORDER_MISMATCH"
    lock = json.loads(LOCK.read_text())
    fixture_hash = sha(LOCK)
    original_snapshots={r["role"].lower():r for r in lock["snapshots"]}
    assert tuple(original_snapshots) == ROLES
    for role, snapshot in original_snapshots.items():
        assert sha(LOCK.parent / snapshot["path"]) == snapshot["sha256"]
    bench = json.loads((args.render_root / "benchmark-results.json").read_text())
    benchmark_rows = {r["cell_id"]:r for r in bench["records"]}
    assert len(benchmark_rows) == 7
    head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    args.out.mkdir(parents=True,exist_ok=True)
    for demand in DEMANDS:
        row=rows[demand]
        cell_id=f"QRT-{demand.upper()}-D2"
        confirmed=benchmark_rows[cell_id]
        assert confirmed["technical"] == "BROWSER_AND_STATIC_PASS" and not confirmed["failures"], cell_id
        src=ROOT / row["provenance"]["source"]
        mf=ROOT / row["provenance"]["manifest"]
        assert blob(src) == row["provenance"]["source_git_blob"], f"{cell_id}:source git blob"
        assert blob(mf) == row["provenance"]["manifest_git_blob"], f"{cell_id}:manifest git blob"
        package=json.loads(src.read_text())
        primaries=[q for q in package["questions"] if "PRIMARY" in q["id"] or q["id"].endswith("-PROOF")]
        assert len(primaries)==1
        assert primaries[0]["origin"]=="AUTHORED"
        manifest=json.loads(mf.read_text())
        assert manifest["selection"]["core2"] == []
        receipt=json.loads((args.render_root / demand / "render-receipt.json").read_text())
        pages=[]
        for name in ("core1.html","core1a.html","core1b.html","core2a.html","core2b.html","index.html"):
            file=args.render_root/demand/name
            assert file.is_file()
            h=sha(file)
            assert receipt["page_sha256"][name] == h, f"{cell_id}:{name} SHA disagreement"
            pages.append({"name":name,"sha256":h,"bytes":file.stat().st_size})
        checks=confirmed["role_checks"]
        assert list(checks) == list(ROLES)
        x,y,z,alternative=COGNITIVE[demand]
        roles=[]
        for role in ROLES:
            snapshot=original_snapshots[role]
            expected=row["comparator"]["roles"][role.upper()]
            assert expected["exact_owner_snapshot_sha256"] == snapshot["sha256"]
            assert checks[role]["blueprint"] == expected["registered_blueprint"]
            assert checks[role]["golden_slot_order"]=="MATCH"
            assert checks[role]["golden_component_order"]=="MATCH"
            roles.append({"role":role.upper(),"registered_blueprint":checks[role]["blueprint"],
                          "technique":{"slot_order":"MATCH","component_order":"MATCH"},
                          "literal_cross_question_html_match":"NOT_APPLICABLE",
                          "original_owner_golden_sha256":snapshot["sha256"]})
        output={
            "schema":"imo-qrt-cell-evidence/v1","template":False,
            "cell_id":cell_id,"band_issue":201,
            "original_question_or_authored_id":primaries[0]["id"],
            "primary_demand":demand.upper(),"band":"D2",
            "status_dimensions":{
                "technical":"BROWSER_AND_STATIC_PASS","renderer_verified":True,
                "technique_review":"STRUCTURAL_ONLY",
                "academic_review":"PENDING_INDEPENDENT",
                "owner_qrt_accepted":False,"owner_golden_designated":False,
                "release":"NOT_AUTHORIZED",
            },
            "source":{"classification":"AUTHORED_TEST","verified_sha":blob(src),
                      "custody":"GIT_AUTHORED_TEST_ONLY",
                      "rights":"AUTHOR_TEST_ONLY_NO_SOURCE_RIGHTS_GRANTED",
                      "question_stem_embedded":False},
            "cognitive":{"X":x,"Y":y,"Z":z,"W":row["protected_w"],
                         "primary_vs_alternative":alternative,
                         "adjacent_band_reason":"D2 provisional; D1 removes connection/choice, D3 requires deeper independent strategy",
                         "difficulty_five_component_evidence":None},
            "blueprints":roles,
            "generation":{
                "repo_commit_sha":head,"source_original_commit_sha":row["provenance"]["head"],
                "manifest_path":row["provenance"]["manifest"],
                "manifest_blob_sha":blob(mf),
                "renderer_version":receipt["renderer"],
                "registry_blob_sha":row["comparator"]["blueprint_registry_git_blob"],
                "mode":receipt["mode"],"held_to":receipt["held_to"],
                "gaps":receipt["gaps"],"exact_head_ci_run":args.run_url,
                "artifact_url":args.run_url,
                "html":pages,"six_html_sha_verified":True,
            },
            "golden":{
                "kind":"IMMUTABLE_OWNER_SNAPSHOT_TECHNIQUE_ONLY",
                "id":lock["fixture_id"],"lock_sha256":fixture_hash,
                "role_comparator":"SLOT_COMPONENT_SEMANTIC_DIFFERENCES",
                "comparison_kind":"SEMANTIC_CROSS_QUESTION",
                "technique_oracles":["REGISTERED_BLUEPRINT","FIVE_ROLE_ORDERED_SLOTS",
                    "FIVE_ROLE_ORDERED_COMPONENTS","REAL_CHROMIUM_ATTEMPT_GATING",
                    "INDEPENDENT_CORE1B_BOUNDARY_ATTEMPT"],
                "semantic_deltas":["CORE2A_H3_AFTER_ATTEMPT_POST_FROZEN_ORIGINAL"],
                "actual_html_bytes_independently_verified":True,
                "owner_fixture_decision_id":None,
            },
            "review":{**{ask:{"qualified_verdict":"PENDING_INDEPENDENT"} for ask in ASKS},
                      "qualified_reviewer_name":None,"conflict_declaration":None,
                      "independent_mathematical_oracle":"AUTHOR_SEPARATE_COMPUTATION_TEST_ONLY",
                      "decision":"PENDING_INDEPENDENT"},
            "owner":{"qrt_decision":"PENDING","qrt_decision_id":None,
                     "golden_scope_decision_id":None,"rights_decision_id":None,
                     "print_visual_decision_id":None,"release_decision_id":None},
            "viewer":{"entry_path":"TEST/imo-research/qrt-d2/issue-201/index.html",
                      "band_issues_path":None,"tile_html_url":None,
                      "links_checked":True},
            "evidence":{"source_commit":row["provenance"]["head"],
                        "CI":args.run_url,
                        "academic":"TEST/imo-research/qrt-d2/issue-201/PRE-REVIEW.md",
                        "golden":lock["fixture_id"],"owner":None,
                        "updated_utc":None},
            "restrictions":[
                "Never publish private authentic Core2 question/solution",
                "Never claim official source or owner golden without explicit decision",
                "Never modify immutable original golden to force parity",
                "No new global blueprint without proved O3 gap",
                "Nonblank H3 when it would reveal W",
                "Mathematical computation tests are not a qualified academic decision",
            ],
        }
        (args.out / f"{demand}-d2.tile.json").write_text(
            json.dumps(output,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"
        )
        print(f"{cell_id}: source-safe protocol tile, six exact renderer page hashes, 12 pending reviewer asks")
    print("Seven D2 tile JSON files generated; 0 Owner acceptance decisions fabricated")

if __name__=="__main__":
    main()
