#!/usr/bin/env python3
"""IMO #182: RETRIEVE-D2 native five-Core golden and method-cue falsifier.

Tests the hypothesis that Core2A demands *unprompted retrieval* of a relationship
rather than execution of an already selected right-triangle method. An explicit
method cue is a falsifier of the stronger unprompted claim, NOT a signed QRT
RECLASSIFY verdict. No source, Owner golden, blueprint or renderer is edited.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import threading
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright
from o1_model_d2_five_core import RootAssets, structural, BP, TECH

SOURCE_HEAD = "5b382356e792ae50884241fb047c328e304d011d"
SOURCE_BLOB = "15333326a90763160d2ff52a32ec579218ed9ac8"
MANIFEST_BLOB = "403d4fbd15dcd47cae0c656289e14564e640e220"
REGISTRY_BLOB = "591ba061b8771c30fdffc4506aa720ca9ba89335"
GOLDEN_LOCK_BLOB = "888678554c41257e6d96c802f0009983ccbb5328"
ROLES = ("core1", "core1a", "core1b", "core2a", "core2b")
PRIMARY = "Q-TEST-QRT-RETRIEVE-D2-PRIMARY"
TRANSFER = "Q-TEST-QRT-RETRIEVE-D2-TRANSFER"
RELATION_CUE = re.compile(r"\b(?:retrieve|use|apply|recall)\b.{0,50}\b(?:right.triangle|pythagor)", re.I)
FORMULA_CUE = re.compile(r"(?:d\s*[²^]\s*2?\s*=|hypotenuse.{0,30}squares?|squares?.{0,45}diagonal)", re.I)
ANSWER_LEAK = ("15m diagonal", "diagonal15m", "diagonal=15", "21m boundary",
               "edge21m", "saving6m", "saving 6m", "15≤18<21", "15 <= 18 < 21")
INVERSE_LEAK = ("other side12m", "missing side12m", "boundary17m", "saves4m",
                "13≤15<17", "13 <= 15 < 17")

def need(ok, message):
    if not ok:
        raise AssertionError(message)

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git_blob(root, path):
    return subprocess.check_output(
        ["git", "hash-object", str(path.relative_to(root))], cwd=root, text=True
    ).strip()

def check_pins(root):
    need(subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root,
                                 text=True).strip() == SOURCE_HEAD,
         "D2 source checkout is not the pinned #205 head")
    paths = {
        "source": root / "TEST/imo-research/qrt-d2/retrieve.v1.json",
        "manifest": root / "TEST/products/imo182-qrt-d2-retrieve.manifest.json",
        "registry": root / "Shared/web/interactive-page-blueprints.v1.json",
        "lock": root / "golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshot-lock.json",
    }
    for name, sha in (("source", SOURCE_BLOB), ("manifest", MANIFEST_BLOB),
                      ("registry", REGISTRY_BLOB), ("lock", GOLDEN_LOCK_BLOB)):
        need(git_blob(root, paths[name]) == sha,
             "STOP: pinned D2 " + name + " differs; do not silently repin")
    obj = {k: read(v) for k, v in paths.items()}
    package, product = obj["source"], obj["manifest"]
    need(package["subject"] == "TEST" and package["status"] == "CANDIDATE",
         "source is no longer held TEST candidate")
    need(package.get("extensions", {}).get("grade9v3:qrt_admitted", False) is False,
         "source unexpectedly marks QRT admitted")
    need(product["subject"] == "TEST" and product["selection"]["core2"] == []
         and tuple(x.lower() for x in product["output_roles"]) == ROLES,
         "manifest no longer has exactly five authored TEST roles")
    need(product["selection"]["core2a"] == [PRIMARY]
         and product["selection"]["core2b"] == [TRANSFER],
         "manifest selected another question")
    need(obj["registry"]["registry_version"] == "1.17.0"
         and obj["lock"]["fixture_id"] == "G-IMO-G9-FIVE-CORE-20261012",
         "registry/golden identity drift")
    return obj, paths

def independent_math():
    def routes(a, b, limit):
        squared = a*a + b*b
        diagonal = math.isqrt(squared)
        need(diagonal*diagonal == squared, "integer Pythagorean triple drift")
        edge = a+b
        return (diagonal, edge, edge-diagonal,
                diagonal <= limit, edge <= limit)
    need(routes(6, 8, 12) == (10, 14, 4, True, False), "worked math")
    need(routes(9, 12, 18) == (15, 21, 6, True, False), "primary math")
    need(routes(8, 15, 20) == (17, 23, 6, True, False), "Core1A exit math")
    need(routes(12, 16, 23) == (20, 28, 8, True, False), "Core1B task math")
    need(routes(8, 15, 20)[1] > 20, "closed-shortcut boundary")
    other = math.isqrt(13*13-5*5)
    need(other == 12 and 13*13 == 5*5+other*other
         and routes(5, other, 15) == (13, 17, 4, True, False),
         "inverse transfer math")
    return {"worked": [10,14,4], "primary": [15,21,6],
            "core1a_changed_exit": [17,23,6],
            "core1b_main": [20,28,8],
            "core1b_boundary_allowed_route": "NONE: diagonal closed, edge23>20",
            "core2b_missing_side": 12, "core2b_routes": [13,17,4],
            "status": "ARITHMETIC_VERIFIED_NOT_ACADEMIC_CLASSIFICATION"}

def method_cues(package):
    qs = {q["id"]: q for q in package["questions"]}
    p, t = qs[PRIMARY], qs[TRANSFER]
    need(p["extensions"]["grade9v3:cognitive_demand"]["primary"] == "RETRIEVE"
         and p["difficulty"]["band"] == "D2", "not declared RETRIEVE-D2")
    need(p["answer"]["crux_move_ref"] == "MOVE-RT-COMBINED",
         "primary protected-W ref changed")
    need(t["transfer"]["builds_on"] == [PRIMARY]
         and t["answer"]["crux_move_ref"] == "MOVE-RT-INVERSE",
         "reverse transfer protected W changed")
    stem = p["stem"]
    h2 = p["scaffolds"][1]["text"]
    prior = " ".join(x["action"] for x in
                     package["microtopics"][0]["teaching_path"])
    observed = {
        "primary_method_named": bool(RELATION_CUE.search(stem)),
        "primary_execution_command": bool(re.search(r"calculate\s+BOTH\s+routes", stem, re.I)),
        "prior_construction_teaches_relation": "d²=6²+8²" in prior,
        "h2_prompts_squares_to_diagonal_relation": bool(FORMULA_CUE.search(h2)),
        "transfer_inverse_method_named": bool(re.search(
            r"right.triangle relation IN REVERSE", t["stem"], re.I)),
    }
    need(all(observed.values()),
         "method-cue control lost a predicate: inspect source, do not silently PASS")
    # Adversarial mutation controls: a candidate with no named relation must
    # not be labelled cued; an explicitly supplied formula must be detected.
    neutral = ("A rectangle has 9m and 12m sides. Choose an appropriate "
               "relationship to compare the direct and edge routes.")
    supplied = "Use Pythagoras d²=a²+b² for the diagonal and add edges."
    need(not RELATION_CUE.search(neutral) and RELATION_CUE.search(supplied),
         "mutation control fails to discriminate retrieval from supplied method")
    return {"source_cue_predicates": observed,
            "uncued_control_detected": False,
            "supplied_method_control_detected": True,
            "mechanical_falsifier": "METHOD_AND_SEQUENCE_SUPPLIED_IN_PRIMARY_STEM",
            "learner_owned_unprompted_retrieval_demonstrated": False,
            "meaning": "Fails to demonstrate unaided relationship selection; "
                       "correct arithmetic or hints do not prove RETRIEVE.",
            "strongest_rival": "APPLY",
            "demand_decision": "HOLD_FOR_INDEPENDENT_REVIEW_ISSUE_211"}

def native_roles(root, obj, paths):
    output = root / "build/imo182-qrt/d2/retrieve"
    receipt = read(output/"render-receipt.json")
    need(receipt["renderer"] == "render_core/2" and receipt["mode"] == "PAGES"
         and receipt["held_to"] == "REFERENCE" and receipt["gaps"] == [],
         "not zero-gap native reference renderer output")
    by_id = {b["id"]: b for b in obj["registry"]["blueprints"]}
    rows = []
    for role in ROLES:
        filename = role+".html"
        page = output/filename
        gold_row = next(x for x in obj["lock"]["snapshots"]
                        if x["role"] == role.upper())
        gold_path = paths["lock"].parent/gold_row["path"]
        need(digest(gold_path) == gold_row["sha256"],
             role+": immutable golden bytes changed")
        need(digest(page) == receipt["page_sha256"][filename],
             role+": native HTML differs from renderer receipt")
        a,b = structural(page),structural(gold_path)
        ident,version = BP[role].split("@")
        bp = by_id[ident]
        need(bp["status"] == "ACTIVE" and bp["version"] == version
             and bp["core_roles"] == [role.upper()],
             role+": registered blueprint changed")
        need(a.roles[:1] == b.roles[:1] == [role.upper()]
             and a.bps == b.bps == [BP[role]]
             and a.slots == b.slots and a.components == b.components,
             role+": registered blueprint slot/component differs from original")
        if role == "core1b":
            need(a.blocks == b.blocks and len(a.blocks) == 13,
                 "Core1B original 13-block reconstruction changed")
        rows.append({"role":role.upper(),"blueprint":BP[role],
                     "techniques":TECH[role],
                     "native_sha256":digest(page),
                     "receipt_match":True,
                     "frozen_original_sha256":gold_row["sha256"],
                     "golden_slots":"MATCH",
                     "golden_components":"MATCH",
                     "golden_blocks":("MATCH" if a.blocks == b.blocks
                                      else "CONTEXTUAL_DIFFERENCE"),
                     "mathematical_teaching_semantics":"PENDING_INDEPENDENT_REVIEW"})
    need(digest(output/"index.html") == receipt["page_sha256"]["index.html"],
         "native index did not match renderer receipt")
    return rows, receipt

def browser(root, report_dir):
    http = ThreadingHTTPServer(
        ("127.0.0.1", 0), partial(RootAssets, directory_root=root))
    worker = threading.Thread(target=http.serve_forever, daemon=True)
    worker.start()
    rows = []
    try:
        with sync_playwright() as pw:
            client = pw.chromium.launch(headless=True, args=["--no-sandbox"])
            try:
                for role in ROLES:
                    for width in (390,768,1280):
                        page = client.new_page(viewport={"width":width, "height":900})
                        errors=[]
                        page.on("pageerror", lambda exc: errors.append(str(exc)))
                        target = (f"http://127.0.0.1:{http.server_port}"
                                  f"/build/imo182-qrt/d2/retrieve/{role}.html")
                        response=page.goto(target, wait_until="load")
                        need(response and response.status==200, role+": HTTP failed")
                        need(page.locator(f"html[data-g9-role='{role.upper()}']").count()==1
                             and page.locator("body[data-blueprint-ref]").get_attribute(
                                 "data-blueprint-ref")==BP[role],
                             role+": wrong registered role")
                        article=page.locator("article[data-g9-unit]").first
                        need(article.count()==1 and article.is_visible(),
                             role+": no actual learner article")
                        styles=page.evaluate("""() => [...document.querySelectorAll(
                            'link[rel=stylesheet]')].map(x=>Boolean(x.sheet))""")
                        need(len(styles)>=2 and all(styles),
                             role+": real repository CSS was not loaded")
                        need(page.evaluate(
                            "() => document.documentElement.scrollWidth <= innerWidth + 2"),
                             role+": horizontal overflow")
                        graphics=article.locator("svg[role=img]").evaluate_all(
                            """nodes => nodes.map(x=>({
                            name:x.getAttribute('aria-label')||'',
                            title:x.querySelector('title')?.textContent||'',
                            desc:x.querySelector('desc')?.textContent||'',
                            stages:[...x.querySelectorAll('[data-g9-stage-id]')]
                             .map(y=>y.getAttribute('data-g9-stage-id'))
                            }))""")
                        need(all(g["name"] or g["title"] for g in graphics),
                             role+": unnamed SVG")
                        rec={"role":role.upper(),"viewport":width,
                             "native_http_and_css":True,
                             "svg_accessibility":graphics,
                             "horizontal_overflow":False}
                        if role=="core1":
                            need(article.locator("[data-g9-block='governing_relation']").count()>=1,
                                 "Core1 prerequisite bridge absent")
                        if role=="core1a":
                            exit_area=article.locator("[data-g9-block='exit_task']")
                            need(exit_area.count()==1 and "15" in exit_area.inner_text()
                                 and "20" in exit_area.inner_text(),
                                 "Core1A independent 8×15 /20m exit absent")
                            rec["changed_case_exit_present"]=True
                        if role=="core1b":
                            need(article.locator("[data-g9-block='boundary_test']").count()==1,
                                 "Core1B separate closed-shortcut boundary absent")
                        if role in ("core2a","core2b"):
                            pre=article.inner_text().lower()
                            ax=" ".join((g["name"]+" "+g["title"]+" "+g["desc"])
                                         for g in graphics).lower()
                            leaks=ANSWER_LEAK if role=="core2a" else INVERSE_LEAK
                            need(not any(s in pre+" "+ax for s in leaks),
                                 role+": protected computed result leaked before commitment")
                            rec["known_full_answer_sentinels_absent"]=True
                            if role=="core2a":
                                stem=article.locator("[data-g9-block='stem']").first.inner_text()
                                need(bool(RELATION_CUE.search(stem))
                                     and bool(re.search(r"calculate\s+BOTH\s+routes",stem,re.I)),
                                     "actual learner stem does not reproduce supplied-method cue")
                                rec["actual_stem_method_cue"]="SUPPLIED"
                        shot=report_dir/"screenshots"/f"{role}-{width}-initial.png"
                        shot.parent.mkdir(parents=True,exist_ok=True)
                        page.screenshot(path=str(shot),full_page=True,
                                        animations="disabled")
                        rec["initial_screenshot_sha256"]=digest(shot)
                        if width==390 and role!="core1":
                            gates=article.locator("details[data-g9-reveal][data-requires-attempt]")
                            need(gates.count()>=1 and all(
                                not x.strip() for x in gates.locator(
                                    "[data-g9-payload-slot]").all_inner_texts()),
                                 role+": response materialised without attempt")
                            need(all(gates.nth(i).get_attribute("data-locked") is not None
                                     for i in range(gates.count())),
                                 role+": gate unlocked initially")
                            attempt=article.locator(
                                "[data-g9-attempt-box]:not([data-g9-attempt-stage='boundary'])").first
                            if attempt.count()==0:attempt=article
                            button=attempt.locator("button[data-g9-commit]").first
                            answer=attempt.locator("textarea[data-g9-attempt]").first
                            need(button.count()==1 and answer.count()==1,
                                 role+": written attempt controls missing")
                            if role=="core2a":
                                initial=article.inner_text()
                                hint=article.get_by_role("button",name="Next hint")
                                need(hint.count()==1,"Core2A next hint missing")
                                hint.click()
                                supported=article.inner_text()
                                delta=[x.strip() for x in supported.splitlines()
                                       if len(x.strip())>20 and x.strip()
                                       not in initial.splitlines()]
                                need(delta,"Core2A no progressive H2")
                                need(not any(s in supported.lower() for s in ANSWER_LEAK),
                                     "Core2A H2 exposed computed answer")
                                need(any("square" in s.lower() for s in delta),
                                     "Core2A H2 expected theorem prompt absent")
                                rec["actual_preattempt_h2_added_text"]=delta
                                h3=article.locator(
                                    'details[data-g9-payload-ref*="after-attempt-hint-3"]')
                                need(h3.count()==1 and h3.get_attribute(
                                    "data-locked") is not None, "Core2A H3 premature")
                            button.click()
                            need(all(gates.nth(i).get_attribute("data-locked") is not None
                                     for i in range(gates.count())),
                                 role+": blank response unlocked answer")
                            answer.fill("I will select the direct and edge routes, "
                                        "form a relevant relationship and check the travel limit.")
                            button.click()
                            need(gates.first.get_attribute("data-locked") is None,
                                 role+": nonblank committed response did not unlock")
                            rec["blank_and_nonblank_attempt_gates"]="PASS"
                            if role=="core1b":
                                boundary=article.locator(
                                    "details[data-g9-attempt-stage='boundary'][data-requires-attempt]")
                                box=article.locator(
                                    "[data-g9-attempt-box][data-g9-attempt-stage='boundary']")
                                need(boundary.count()==1 and box.count()==1
                                     and boundary.get_attribute("data-locked") is not None,
                                     "Core1B boundary not separately gated")
                                box.locator("button[data-g9-commit]").click()
                                need(boundary.get_attribute("data-locked") is not None,
                                     "blank boundary incorrectly unlocked")
                                box.locator("textarea[data-g9-attempt]").fill(
                                    "Only the boundary route is allowed; its length exceeds 20m.")
                                box.locator("button[data-g9-commit]").click()
                                need(boundary.get_attribute("data-locked") is None,
                                     "Core1B nonblank boundary did not unlock")
                                rec["independent_boundary_commit"]="PASS"
                            if role=="core2a":
                                need(h3.get_attribute("data-locked") is None,
                                     "post-attempt H3 stayed locked")
                                h3.locator("summary").click()
                                need(article.locator("[data-g9-after-attempt-hint]").is_visible(),
                                     "H3 not visible after commitment")
                                rec["post_attempt_h3"]="PASS"
                        need(not errors,role+": browser uncaught exception "+repr(errors))
                        rows.append(rec)
                        page.close()
            finally:
                client.close()
    finally:
        http.shutdown();http.server_close();worker.join(timeout=5)
    need(len(rows)==15,"missing one or more actual five-role/three-viewport probes")
    return rows

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--repo",required=True,type=Path)
    args=parser.parse_args()
    root=args.repo.resolve()
    obj,paths=check_pins(root)
    cues=method_cues(obj["source"])
    math_witness=independent_math()
    roles,receipt=native_roles(root,obj,paths)
    report_dir=root/"build/imo182-qrt/d2-retrieve-method-cue"
    observed=browser(root,report_dir)
    report={
        "schema":"imo182-retrieve-d2-five-core-method-cue/v1",
        "cell":"QRT-RETRIEVE-D2",
        "source_head":SOURCE_HEAD,
        "source_blob":SOURCE_BLOB,
        "manifest_blob":MANIFEST_BLOB,
        "registry_blob":REGISTRY_BLOB,
        "frozen_golden_lock_blob":GOLDEN_LOCK_BLOB,
        "renderer":"render_core/2",
        "native_six_html_sha_verified":True,
        "render_receipt_page_sha256":receipt["page_sha256"],
        "five_original_blueprints_and_golden_techniques":roles,
        "independent_math":math_witness,
        "method_cue_falsifier":cues,
        "native_three_viewport_browser":observed,
        "learner_w_hypothesis":"Learner independently chooses a right-triangle "
          "relationship rather than being directed to execute it.",
        "learner_y_prior_relation_status":"UNCERTAIN_NOT_OBSERVED_WITH_LEARNERS",
        "engineering_risk":"SOURCE_INPUT_CUES_THE_RELATION_AND_EXECUTION_SEQUENCE",
        "semantic_verdict_for_primary_unprompted_retrieval":"DEFECT",
        "academic_primary_demand":"PENDING_QUALIFIED_REVIEW_RETRIEVE_VS_APPLY",
        "difficulty_five_factors":"AUTHOR_PROPOSAL_NOT_INDEPENDENT",
        "all_12_HSPM":"PENDING_QUALIFIED_REVIEW",
        "signed_independent_academic_verdict":None,
        "owner_qrt_decision_id":None,
        "owner_accepted":False,
        "golden_designation":None,
        "o3_blueprint_change_authorized":False,
        "source_revision_authorized":False,
        "authentic_core2_admitted":0,
        "public_release_authorized":False,
        "note":"Falsifies only the *unprompted relationship retrieval* claim for "
          "these rendered pages. It does not automatically decide the QRT label, "
          "learner knowledge, difficulty, mathematics pedagogy or Owner acceptance."
    }
    report_dir.mkdir(parents=True,exist_ok=True)
    out=report_dir/"retrieve-d2-five-core-method-cue.v1.json"
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",
                   encoding="utf-8")
    print("O1 RETRIEVE-D2: six SHA-bound native HTML pages, "
          "five frozen structural golden roles and computed math PASS")
    print("O1 RETRIEVE-D2: method-cue negative control "
          "FALSIFIES unprompted retrieval claim; APPLY rival remains reviewer HOLD")
    print("O1 RETRIEVE-D2: 15 browser role/viewport checks and attempt controls PASS")
    print("REPORT",out)

if __name__=="__main__":
    main()
