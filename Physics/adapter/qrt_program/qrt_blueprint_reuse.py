"""Physics-only READ-ONLY composition of canonical 28 QRT semantics and Core roles.

Use existing Physics source crosswalk; never implement another QRT scorer,
renderer, learner-exposure test or Physics oracle. Candidate only, not Pass-A
blind reviewer input, not the 28-item Mathematics/IMO TEST adoption ledger.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from Physics.adapter.qrt_program.qrt_crosswalk import inspect_question

ROOT = Path(__file__).resolve().parents[3]
WITNESSES = "tools/physics_qrt_program/witnesses.candidate.v1.json"
REGISTRY = "Shared/web/interactive-page-blueprints.v1.json"
TEMPLATES = "Shared/quality/question-demand-templates.v1.json"
ROLES = ("CORE1","CORE1A","CORE1B","CORE2A","CORE2B")
DEMANDS = ("RETRIEVE","EXPLAIN","APPLY","MODEL","REPRESENT","SYNTHESIZE","JUSTIFY")
BANDS = ("D1","D2","D3","D4")
ASKS = ("H1","H2","H3","S1","S2","S3","P1","P2","P3","M1","M2","M3")
ACTIVE = "Q-PHY-NLM-2B-FRICTION-STATE-01"
BASE = "73c66b64158ee2ff57b099f990e1c2081d5c571f"
HEX40 = re.compile(r"^[0-9a-f]{40}$")

class ReuseBlocked(ValueError):
    pass

def require(ok, reason):
    if not ok: raise ReuseBlocked(reason)

def blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()

def read_json(root, name):
    candidate = (root/name).resolve()
    require(candidate.is_relative_to(root.resolve()) and candidate.is_file(),
            "SOURCE_FILE_MISSING:"+name)
    raw = candidate.read_bytes()
    return json.loads(raw), {"path":name,"git_blob_sha":blob(raw),
                             "sha256":hashlib.sha256(raw).hexdigest()}

def map_reuse(root:Path=ROOT):
    """All conclusions are source-classified and blocked, regardless of green CI."""
    w, wsource = read_json(root,WITNESSES)
    registry, bsource = read_json(root,REGISTRY)
    templates, tsource = read_json(root,TEMPLATES)
    require(w.get("schema")=="physics-qrt.witness-candidates/v1" and
            w.get("programme")=="PHY-QRT-LTA-v1" and
            w.get("base_sha")==BASE and w.get("stage")=="CANDIDATE_NOT_FROZEN",
            "WITNESS_CONTRACT_OR_SOURCE_CUT_DRIFT")
    require(registry.get("schema_version")=="1.0" and registry.get("registry_version"), "BLUEPRINT_SCHEMA_DRIFT")
    require(templates.get("schema")=="question-demand-templates/v1", "QRT_TEMPLATE_SCHEMA_DRIFT")
    entries=templates.get("templates")
    require(isinstance(entries,list),"QRT_TEMPLATES_MISSING")
    keys=[row.get("template_id") for row in entries]
    expected={f"QRT-{d}-{band}" for d in DEMANDS for band in BANDS}
    require(len(keys)==28 and len(set(keys))==28 and set(keys)==expected,
            "SHARED_28_QRT_CATALOGUE_DRIFT")
    for t in entries:
        require(tuple((t.get("review") or {}).keys())==ASKS,"CANONICAL_12_ASKS_DRIFT")
        require(all((t.get("slots") or {}).get(k) for k in ("X","Y","Z","W")),
                "QRT_PROTECTED_WORK_MISSING")
    bps=registry.get("blueprints")
    require(isinstance(bps,list) and len(bps)==7,"REGISTERED_7_BLUEPRINTS_DRIFT")
    byrole={}
    for bp in bps:
        require(bp.get("status")=="ACTIVE" and bp.get("id") and bp.get("version"),
                "BLUEPRINT_NOT_ACTIVE")
        for role in bp.get("core_roles",[]):
            require(role not in byrole,"DUPLICATE_CORE_BLUEPRINT_ROLE")
            byrole[role]={"role":role,"blueprint":bp["id"]+"@"+bp["version"],
                          "availability":"REGISTERED_ONLY_NOT_RENDER_ATTESTATION"}
    require(set(byrole)==set(ROLES)|{"CORE2","EXPLORER"},
            "EXPECTED_CORE_ROLE_BLUEPRINTS_MISSING")
    cases=w.get("cases")
    require(isinstance(cases,list) and len(cases)==4,"FOUR_CANDIDATE_WITNESSES_REQUIRED")
    ids=[c.get("question_id") for c in cases]
    require(len(set(ids))==4 and ids.count(ACTIVE)==1,
            "NLM_ONE_ACTIVE_PILOT_REQUIRED")
    rows=[]
    for witness in cases:
        path=witness.get("package")
        qid=witness.get("question_id")
        require(isinstance(path,str) and path.startswith("Physics/library/") and
                ".." not in Path(path).parts,"PHYSICS_LIBRARY_ONLY")
        require(isinstance(qid,str) and qid.startswith("Q-PHY-"),"PHYSICS_QUESTION_ONLY")
        require(isinstance(witness.get("source_blob_sha"),str) and
                HEX40.fullmatch(witness["source_blob_sha"]),
                "MISSING_ORIGINAL_PACKAGE_BLOB")
        source=inspect_question(path,qid,root=root)
        require(source["status"]=="SOURCE_STRUCTURALLY_BOUND_NOT_ACCEPTED" and
                source["package_blob_sha"]==witness["source_blob_sha"],
                "SOURCE_ORIGINAL_BLOB_OR_CUSTODY_DRIFT:"+qid)
        require(source["primary_capability_ref"]==witness["expected_capability"],
                "CAPABILITY_MAPPING_DRIFT:"+qid)
        require(witness["expected_core"] in source["declared_cores"],
                "OWNING_CORE_MAPPING_DRIFT:"+qid)
        source_gate=source["qrt_source_gate"]
        declared=source_gate["declared_demand"]
        band=source.get("difficulty",{}).get("band") if isinstance(source.get("difficulty"),dict) else None
        proposed_key=f"QRT-{declared}-{band}" if declared in DEMANDS and band in BANDS else None
        # A structural source record is NOT an independent QRT/Physics result.
        # The actual current Physics witnesses lack source-approved cognitive demand.
        if source_gate["state"]=="BLOCKED":
            proposed_key=None
        exact_roles=[dict(byrole[k]) for k in ROLES]
        rows.append({
            "question_id":qid,
            "review_scope":"ACTIVE_SINGLE_NLM_OPTION_A" if qid==ACTIVE else "RESERVED_REFERENCE_NOT_REVIEW_SCOPE",
            "source":{"path":path,"base_sha":BASE,
                      "git_blob_sha":source["package_blob_sha"],
                      "sha256":source["package_sha256"],
                      "origin":source["source_class"]},
            "primary_capability_ref":source["primary_capability_ref"],
            "declared_question_cores":source["declared_cores"],
            "canonical_five_factor_difficulty":band,
            "qrt_source_gate":source_gate,
            "qrt_cell":proposed_key,
            "qrt_assignment_status":"ACADEMICALLY_NOT_QUALIFIED" if proposed_key
                else "UNRESOLVED_COGNITIVE_DEMAND_HOLD",
            "five_registered_role_blueprints":exact_roles,
            "native_five_page_evidence":"NOT_RECOMPUTED_BY_THIS_MAP",
            "physics_oracle":"PENDING_AUTHENTICATED_INDEPENDENT_REVIEW",
            "review_asks":{a:"NOT_RUN_FOR_THIS_QUESTION" for a in ASKS},
            "independent_reviewer":"UNASSIGNED",
            "owner_accepted":False,
            "published":False,
        })
    return {
        "schema":"physics-qrt.shared-reuse-evidence/v1",
        "kind":"SOURCE_REFERENCED_CANDIDATE_ONLY_NOT_FOR_BLIND_PASS_A",
        "canonical_pointers":{"witnesses":wsource,"blueprints":bsource,"qrt_templates":tsource},
        "summary":{"shared_qrt_semantic_templates":28,"registered_core_blueprints":7,
                   "candidate_physics_questions":4,"active_academic_pilot":1,
                   "reserved_reference_questions":3,
                   "registered_role_links":len(rows)*len(ROLES),
                   "actually_rendered_role_pages_proven_by_this_map":0,
                   "academically_accepted_physics_questions":0},
        "rows":rows,
        "core_engine_unchanged":True,
        "new_blueprints_created":0,
        "new_renderer_created":False,
        "qrt_semantic_acceptance":"HOLD",
        "scientific_acceptance":"HOLD",
        "owner_approval":"NOT_GRANTED",
        "release":"HOLD"
    }

def main():
    p=argparse.ArgumentParser(description="Physics QRT 4-source read-only reuse evidence; not academic review")
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    try:
        result=map_reuse(a.root)
        text=json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
        if a.output:
            a.output.parent.mkdir(parents=True,exist_ok=True)
            a.output.write_text(text,encoding="utf-8")
        else: print(text,end="")
        return 0
    except (ReuseBlocked,OSError,ValueError,TypeError,KeyError) as exc:
        print(json.dumps({"status":"BLOCKED","reason":str(exc),"owner_approval":"NOT_GRANTED"}))
        return 2

if __name__=="__main__":raise SystemExit(main())
